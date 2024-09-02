from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import get_user_model
from rest_framework.exceptions import NotFound
from django.contrib.auth import authenticate
from .serializers import RegisterSerializer, LoginSerializer,PasswordResetRequestSerializer, PasswordResetConfirmSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from drf_yasg.utils import swagger_auto_schema
from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from .models import Workspace, Project
from .serializers import WorkspaceSerializer, ProjectSerializer

User = get_user_model()
class RegisterView(APIView):
    @swagger_auto_schema(request_body=RegisterSerializer)
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()

            
            refresh = RefreshToken.for_user(user)
            return Response({
                'message': 'User created successfully',
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }, status=status.HTTP_201_CREATED)
        
        return Response({
            'message': 'Registration failed',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    @swagger_auto_schema(request_body=LoginSerializer)
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']

            
            refresh = RefreshToken.for_user(user)
            return Response({
                'message': 'Login successful',
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }, status=status.HTTP_200_OK)
        
        return Response({
            'message': 'Login failed',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


class PasswordResetRequestView(APIView):
    @swagger_auto_schema(request_body=PasswordResetRequestSerializer)
    def post(self, request):
        serializer = PasswordResetRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        username = serializer.validated_data['username']
        
        try:
            User.objects.get(username=username)
            # Simulate sending a password reset link
            return Response({"message": "success"}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            raise NotFound("User not found")

class PasswordResetConfirmView(APIView):
    @swagger_auto_schema(request_body=PasswordResetConfirmSerializer)
    def post(self, request):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        username = serializer.validated_data['username']
        new_password = serializer.validated_data['new_password']

        try:
            user = User.objects.get(username=username)
            user.set_password(new_password)
            user.save()
            return Response({"message": "Password reset successfully"}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            raise NotFound("User not found")


class WorkspaceViewSet(viewsets.ModelViewSet):
    serializer_class = WorkspaceSerializer
    queryset = Workspace.objects.all()
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)
    
    @action(detail=True, methods=['post'])
    def add_member(self, request, pk=None):

        workspace = self.get_object()
        user_ids = request.data.get('user_ids', [])  # Assume `user_ids` is a list of user IDs provided in the request

        for user_id in user_ids:

            try:

                user = User.objects.get(id=user_id)
                workspace.members.add(user)
            except User.DoesNotExist:

                return Response({'status': f'User with ID {user_id} does not exist'}, status=status.HTTP_400_BAD_REQUEST)

        workspace.save()
        return Response({'status': 'members added'})

    

    


class ProjectViewSet(viewsets.ModelViewSet):
    serializer_class = ProjectSerializer
    queryset = Project.objects.all()
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        workspace = Workspace.objects.get(id=self.request.data['workspace_id'])
        serializer.save(workspace=workspace)
    
