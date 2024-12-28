from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.pagination import PageNumberPagination
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework import viewsets
from rest_framework.filters import SearchFilter, OrderingFilter


from django.shortcuts import get_object_or_404
from django.core.cache import cache
from django.db.models import Q

from .models import Article, Comment
from .serializers import ArticleListSerializer, ArticleDetailSerializer, CommentSerializer



class ArticleListCreate(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]
    pagination_class = PageNumberPagination()

    def get(self, request):
        """게시글 목록 조회"""
        # 쿼리셋 생성
        queryset = Article.objects.all()
        
        # 검색 필터링
        search = request.query_params.get('search', '')
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) |
                Q(content__icontains=search)
            )
        
        # 정렬
        ordering = request.query_params.get('ordering', '')
        if ordering in ['created_at', 'view_count', '-created_at', '-view_count']:
            queryset = queryset.order_by(ordering)
            
        # 페이지네이션
        paginator = self.pagination_class
        paginated_queryset = paginator.paginate_queryset(queryset, request)
        
        # 직렬화
        serializer = ArticleListSerializer(paginated_queryset, many=True)
        
        return paginator.get_paginated_response(serializer.data)
     
        articles = Article.objects.all()
        serializer = ArticleListSerializer(articles, many=True)  # 목록용 Serializer 사용
        return Response(serializer.data)



    def post(self, request):
        """게시글 생성"""
        serializer = ArticleDetailSerializer(data=request.data)  # 상세 Serializer 사용
        if serializer.is_valid():
            serializer.save(author=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ArticleViewSet(viewsets.ModelViewSet):
    pagination_class = PageNumberPagination
    queryset = Article.objects.all()
    serializer_class = ArticleListSerializer

    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['title', 'content']
    ordering_fields = ['created_at', 'view_count']




class ArticleDetail(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_object(self, article_pk):
        return get_object_or_404(Article, pk=article_pk)

    def get(self, request, article_pk):
        """게시글 상세 조회"""
        article = self.get_object(article_pk)
        
        # 로그인한 사용자이고 작성자가 아닌 경우에만 조회수 증가 처리
        # 24시간 동안 같은 IP에서 같은 게시글 조회 시 조회수가 증가하지 않음
        if request.user != article.author:
            # 해당 사용자의 IP와 게시글 ID로 캐시 키를 생성
            cache_key = f"view_count_{request.META.get('REMOTE_ADDR')}_{article_pk}"
            
            # 캐시에 없는 경우에만 조회수 증가
            if not cache.get(cache_key):
                article.view_count += 1
                article.save()
                # 캐시 저장 (24시간 유효)
                cache.set(cache_key, True, 5)
        
        # article.view_count += 1
        # article.save()
        
        serializer = ArticleDetailSerializer(article)  # 상세 Serializer 사용
        return Response(serializer.data)

    def delete(self, request, article_pk):
        """게시글 삭제"""
        article = self.get_object(article_pk)    
        
        # 작성자 본인인지 확인
        if request.user != article.author:
            return Response({'error': '게시글 작성자만 삭제할 수 있습니다.'}, 
                          status=status.HTTP_403_FORBIDDEN)
            
        article.delete()
        return Response({'message': '게시글이 성공적으로 삭제되었습니다.'}, 
                      status=status.HTTP_204_NO_CONTENT)

    def put(self, request, article_pk):
        """게시글 수정"""
        article = self.get_object(article_pk)
        
        # 작성자 본인인지 확인
        if request.user != article.author:
            return Response({'error': '게시글 작성자만 수정할 수 있습니다.'}, 
                          status=status.HTTP_403_FORBIDDEN)
            
        serializer = ArticleDetailSerializer(article, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CommentListCreate(APIView):

    def get_article(self, article_pk):
        return get_object_or_404(Article, pk=article_pk)

    def get(self, request, article_pk):
        """댓글 목록 조회"""
        article = self.get_article(article_pk)
        comments = article.comments.all()
        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data)

    def post(self, request, article_pk):
        """댓글 생성"""
        article = self.get_article(article_pk)
        serializer = CommentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(author=request.user, article=article)
            return Response(serializer.data, 
                          status=status.HTTP_201_CREATED)
        return Response(serializer.errors, 
                      status=status.HTTP_400_BAD_REQUEST)


class CommentLike(APIView):

    def get_article(self, article_pk):
        return get_object_or_404(Article, pk=article_pk)

    def get_comment(self, article, comment_pk):
        return get_object_or_404(Comment, pk=comment_pk, article=article)

    def post(self, request, article_pk, comment_pk):
        """댓글 좋아요 토글"""
        article = self.get_article(article_pk)
        comment = self.get_comment(article, comment_pk)
        user = request.user
        
        # 이미 좋아요를 눌렀는지 확인
        if comment.like_users.filter(pk=user.pk).exists():
            # 좋아요 취소
            comment.like_users.remove(user)
            message = "댓글 좋아요가 취소되었습니다."
        else:
            # 좋아요 추가
            comment.like_users.add(user)
            message = "댓글을 좋아요 했습니다."

        # 댓글 정보를 시리얼라이저를 통해 반환
        serializer = CommentSerializer(comment, context={'request': request})
         
        return Response({
            'message': message,
            'comment': serializer.data
        }, status=status.HTTP_200_OK)


