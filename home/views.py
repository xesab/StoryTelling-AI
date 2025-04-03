from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from transformers import pipeline
from rest_framework import viewsets
from .models import Story, UserStoryInteraction
from .serializers import StorySerializer
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer


# Load T5 model and tokenizer
MODEL_NAME = "google/flan-t5-large"
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModelForSeq2SeqLM.from_pretrained(MODEL_NAME)

class GenerateStoryAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        difficulty = request.data.get("difficulty_level", "beginner")
        user_input = request.data.get("user_input", "")

        if not user_input:
            return Response({"error": "User input is required"}, status=400)

        # Refined prompt to avoid repetition
        prompt = f"Create a {difficulty} level story based on the following: {user_input}. The story should be unique, engaging, and appropriate for a language learning context."

        inputs = tokenizer(prompt, return_tensors="pt", max_length=512, truncation=True)

        # Generate a story with temperature and top-p to control randomness and diversity
        outputs = model.generate(
            **inputs,
            max_new_tokens=200,  # Limit output length
            temperature=0.8,     # Controls randomness (higher is more random)
            top_p=0.9,          # Controls diversity (higher is more diverse)
            do_sample=True      # Enable sampling to allow more diversity in output
        )

        story_text = tokenizer.decode(outputs[0], skip_special_tokens=True)
        title = f"Story by {user} - {user_input}"

        # Save the story
        story = Story.objects.create(user=user, title=title, content=story_text, difficulty_level=difficulty)
        UserStoryInteraction.objects.create(user=user, story=story, user_input=user_input, ai_response=story_text)

        return Response({
            "story_id": story.id,
            "story_title": story.title,
            "story_text": story_text,
            "difficulty_level": difficulty
        })
    
class UserStoryListAPIView(viewsets.ReadOnlyModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = StorySerializer

    def get_queryset(self):
        return Story.objects.filter(user=self.request.user).order_by("-created_at")
    
class ContinueStoryAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, story_id):
        user_input = request.data.get("user_input", "")
        if not user_input:
            return Response({"error": "User input is required"}, status=400)

        try:
            story = Story.objects.get(id=story_id, user=request.user)
        except Story.DoesNotExist:
            return Response({"error": "Story not found"}, status=404)

        # Refined prompt to avoid repetitive responses
        prompt = f"Continue this {story.difficulty_level} level story based on the following text: {story.content} {user_input}. The continuation should be unique and relevant."

        # Tokenize input and generate continuation
        inputs = tokenizer(prompt, return_tensors="pt", max_length=512, truncation=True)

        # Generate continuation with controlled sampling
        outputs = model.generate(
            **inputs,
            max_new_tokens=150,   # Limit length for the continuation
            temperature=0.8,      # Controls randomness of output
            top_p=0.9,            # Controls output diversity
            do_sample=True        # Enables sampling for diversity
        )

        ai_response = tokenizer.decode(outputs[0], skip_special_tokens=True)

        # Save interaction
        UserStoryInteraction.objects.create(user=request.user, story=story, user_input=user_input, ai_response=ai_response)

        # Append the AI response to the story content
        story.content += f"\n\n{ai_response}"
        story.save()

        return Response({
            "story_id": story.id,
            "story_text": story.content
        })