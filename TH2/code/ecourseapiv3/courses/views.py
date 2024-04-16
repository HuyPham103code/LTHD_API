from rest_framework import viewsets, generics, parsers, status, permissions
from courses.models import Category, Course, Lesson, User, Comment, Like
from courses import serializers, paginator, perms
from courses.paginator import CommentPaginator, CoursePaginatior
from rest_framework.response import Response
from rest_framework.decorators import action



class CategoryViewSet(viewsets.ViewSet, generics.ListAPIView):
    queryset = Category.objects.all()
    serializer_class = serializers.CategorySerializer

class CourseViewSet(viewsets.ViewSet, generics.ListAPIView):
    queryset = Course.objects.filter(active=True)
    serializer_class = serializers.CourseSerializer
    pagination_class = CoursePaginatior

    def get_queryset(self):
        queryset = self.queryset
        q = self.request.query_params.get('q')
        if q:
            print(q)
            queryset = queryset.filter(name__icontains=q)
        
        cate_id = self.request.query_params.get('category_id')
        if cate_id:
            queryset = queryset.filter(category_id=cate_id)
        return queryset

class LessonViewSet(viewsets.ViewSet, generics.RetrieveAPIView):
    queryset = Lesson.objects.prefetch_related('tags').filter(active=True)
    serializer_class = serializers.LessonDetailsSerializer

    def get_serializer_class(self):
        if self.request.user.is_authenticated:
            return serializers.Authenticated_LessonDetailsSerializer
        return self.serializer_class

    #   chứng thực
    def get_permissions(self):
        if self.action in ['add_comment']:
            return [permissions.IsAuthenticated(),]
        return [permissions.AllowAny(),]

#   kỹ thuật phân trang
    @action(methods=['get'], url_path='comments', detail=True)
    def get_comment(self, request, pk):
        comments = self.get_object().comment_set.select_related('user').order_by('-id')

        paginator = CommentPaginator()
        page = paginator.paginate_queryset(comments, request)

        if page is not None:
            serializer = serializers.CommentSerializer(page, many=True)
            return paginator.get_paginated_response(serializer.data)

        return Response(serializers.CommentSerializer(comments, many=True).data,
                        status=status.HTTP_200_OK)
    
    @action(methods=['post'], url_path='add-comment', detail=True)
    def add_comment(self, request, pk):
        c = self.get_object().comment_set.create(content=request.data.get('content'),
                                             user=request.user)
        return Response(serializers.CommentSerializer(c).data, status=status.HTTP_201_CREATED)
    
    # @action(methods=['delete'], url_path='delete-comment/(?P<comment_id>\d+)', detail=True)
    # def delete_comment(self, request, pk, comment_id):
        try:
            comment = self.get_object().comment_set.get(pk=comment_id, user=request.user)
            comment.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Comment.DoesNotExist:
            return Response({'message': 'Comment not found or not owned by user'}, status=status.HTTP_404_NOT_FOUND)

    @action(methods=['post'], url_path='like', detail=True)
    def like(self, request, pk):
        li, created = Like.objects.get_or_create(lesson=self.get_object(), user=request.user)

        if not created:
            li.active = not li.active
            li.save()
        return Response(serializers.LessonDetailsSerializer(self.get_object()).data, status=status.HTTP_201_CREATED)




class UserViewSet(viewsets.ViewSet, generics.CreateAPIView):
    queryset = User.objects.filter(is_active=True)
    serializer_class = serializers.UserSerializer
    parser_classes = [parsers.MultiPartParser,]

    def get_permissions(self):
        if self.action in ['get_current_user']:
            return [permissions.IsAuthenticated()]
    [permissions.AllowAny]
    
    @action(methods=['get', 'patch'], url_path='current-user', detail=False)
    def get_current_user(self, request):
        user = request.user
        if request.method.__eq__('PATCH'):
            for k, v in request.data.items():
                setattr(user, k, v)
            user.save()
        return Response(serializers.UserSerializer(user).data)
    

class CommentViewSet(viewsets.ViewSet, generics.DestroyAPIView, generics.UpdateAPIView):
    queryset = Comment.objects.all()
    serializer_class = serializers.CommentSerializer
    permission_classes = [perms.CommentOnwer]

#   xem tới 19.42
