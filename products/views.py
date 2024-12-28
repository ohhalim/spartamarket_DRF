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

from .models import Product, Comment
from .serializers import ProductListSerializer, ProductDetailSerializer, CommentSerializer

class ProductListCreate(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]
    pagination_class = PageNumberPagination()

    def get(self, request):
        """상품 목록 조회"""
        # 쿼리셋 생성
        queryset = Product.objects.all()
        
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
        serializer = ProductListSerializer(paginated_queryset, many=True)
        
        return paginator.get_paginated_response(serializer.data)

    def post(self, request):
        """상품 생성"""
        serializer = ProductDetailSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(author=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ProductViewSet(viewsets.ModelViewSet):
    pagination_class = PageNumberPagination
    queryset = Product.objects.all()
    serializer_class = ProductListSerializer

    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['title', 'content']
    ordering_fields = ['created_at', 'view_count']

class ProductDetail(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_object(self, product_pk):
        return get_object_or_404(Product, pk=product_pk)

    def get(self, request, product_pk):
        """상품 상세 조회"""
        product = self.get_object(product_pk)
        
        if request.user != product.author:
            cache_key = f"view_count_{request.META.get('REMOTE_ADDR')}_{product_pk}"
            
            if not cache.get(cache_key):
                product.view_count += 1
                product.save()
                cache.set(cache_key, True, 5)
        
        serializer = ProductDetailSerializer(product)
        return Response(serializer.data)

    def delete(self, request, product_pk):
        """상품 삭제"""
        product = self.get_object(product_pk)    
        
        if request.user != product.author:
            return Response({'error': '상품 작성자만 삭제할 수 있습니다.'}, 
                          status=status.HTTP_403_FORBIDDEN)
            
        product.delete()
        return Response({'message': '상품이 성공적으로 삭제되었습니다.'}, 
                      status=status.HTTP_204_NO_CONTENT)

    def put(self, request, product_pk):
        """상품 수정"""
        product = self.get_object(product_pk)
        
        if request.user != product.author:
            return Response({'error': '상품 작성자만 수정할 수 있습니다.'}, 
                          status=status.HTTP_403_FORBIDDEN)
            
        serializer = ProductDetailSerializer(product, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CommentListCreate(APIView):
    def get_product(self, product_pk):
        return get_object_or_404(Product, pk=product_pk)

    def get(self, request, product_pk):
        """댓글 목록 조회"""
        product = self.get_product(product_pk)
        comments = product.comments.all()
        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data)

    def post(self, request, product_pk):
        """댓글 생성"""
        product = self.get_product(product_pk)
        serializer = CommentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(author=request.user, product=product)
            return Response(serializer.data, 
                          status=status.HTTP_201_CREATED)
        return Response(serializer.errors, 
                      status=status.HTTP_400_BAD_REQUEST)

class CommentLike(APIView):
    def get_product(self, product_pk):
        return get_object_or_404(Product, pk=product_pk)

    def get_comment(self, product, comment_pk):
        return get_object_or_404(Comment, pk=comment_pk, product=product)

    def post(self, request, product_pk, comment_pk):
        """댓글 좋아요 토글"""
        product = self.get_product(product_pk)
        comment = self.get_comment(product, comment_pk)
        user = request.user
        
        if comment.like_users.filter(pk=user.pk).exists():
            comment.like_users.remove(user)
            message = "댓글 좋아요가 취소되었습니다."
        else:
            comment.like_users.add(user)
            message = "댓글을 좋아요 했습니다."

        serializer = CommentSerializer(comment, context={'request': request})
         
        return Response({
            'message': message,
            'comment': serializer.data
        }, status=status.HTTP_200_OK)


