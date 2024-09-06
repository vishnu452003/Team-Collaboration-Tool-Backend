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

    def get_queryset(self):
        # Return workspaces where the logged-in user is the owner
        return Workspace.objects.filter(owner=self.request.user)
    

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)
    
    @action(detail=True, methods=['post'])
    def add_member(self, request, pk=None):

        workspace = self.get_object()
        usernames = request.data.get('usernames', [])  # Assume `usernames` is a list of user names provided in the request

        for username in usernames:

            try:

                user = User.objects.get(username=username)
                workspace.members.add(user)
            except User.DoesNotExist:

                return Response({'status': f'User with ID {username} does not exist'}, status=status.HTTP_400_BAD_REQUEST)

        workspace.save()
        return Response({'status': 'members added'})

    

    


class ProjectViewSet(viewsets.ModelViewSet):
    serializer_class = ProjectSerializer
    queryset = Project.objects.all()
   

    def perform_create(self, serializer):
        workspace = Workspace.objects.get(id=self.request.data['workspace_id'])
        serializer.save(workspace=workspace)
    
    def get_queryset(self):
        workspace_id = self.request.query_params.get('workspace_id')
        if workspace_id:
            return self.queryset.filter(workspace__id=workspace_id)
        return self.queryset
    
    def update(self, request, *args, **kwargs):
        project = self.get_object()
        project.name = request.data.get('name', project.name)
        project.description = request.data.get('description', project.description)
        project.save()
        serializer = ProjectSerializer(project)
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        project = self.get_object()
        project.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
