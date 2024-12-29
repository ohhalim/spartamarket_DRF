from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.pagination import PageNumberPagination
from django.shortcuts import get_object_or_404
from django.core.cache import cache
from django.db.models import Q

from .models import Product, Comment
from .serializers import ProductListSerializer, ProductDetailSerializer, CommentSerializer

class ProductListCreate(APIView):
    """
    상품 목록 조회(GET)와 상품 생성(POST)을 처리하는 API View
    
    권한 설정 상세 설명:
    1. permission_classes = [IsAuthenticatedOrReadOnly]
       - IsAuthenticatedOrReadOnly: DRF에서 제공하는 기본 권한 클래스
       - 'Read' 작업(GET)은 인증되지 않은 사용자도 허용
       - 'Write' 작업(POST, PUT, DELETE)은 인증된 사용자만 허용
    
    2. 각 HTTP 메서드별 권한:
       - GET (목록 조회): 
         -> 모든 사용자가 접근 가능 (IsAuthenticatedOrReadOnly의 'ReadOnly' 부분)
         -> 비로그인 사용자도 상품 목록을 볼 수 있음
       
       - POST (상품 생성): 
         -> 인증된 사용자만 접근 가능 (IsAuthenticatedOrReadOnly의 'IsAuthenticated' 부분)
         -> 로그인하지 않은 사용자가 POST 요청시 401 Unauthorized 반환
    """
    permission_classes = [IsAuthenticatedOrReadOnly]
    pagination_class = PageNumberPagination()

    def get(self, request):
        """
        상품 목록 조회 API
        - 모든 사용자가 접근 가능 (IsAuthenticatedOrReadOnly의 'ReadOnly' 부분)
        """
        # 전체 상품 목록 가져오기
        products = Product.objects.all()
        
        # 검색어가 있으면 제목이나 내용에서 검색
        search = request.query_params.get('search', '')
        if search:
            products = products.filter(
                Q(title__icontains=search) |
                Q(content__icontains=search)
            )
        
        # 정렬 옵션 처리 (최신순, 조회수순)
        ordering = request.query_params.get('ordering', '')
        if ordering in ['created_at', 'view_count', '-created_at', '-view_count']:
            products = products.order_by(ordering)
            
        # 페이지네이션 적용
        paginator = self.pagination_class
        page = paginator.paginate_queryset(products, request)
        
        # 데이터 직렬화
        serializer = ProductListSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)

    def post(self, request):
        """
        상품 등록 API
        - 로그인한 사용자만 접근 가능 (IsAuthenticatedOrReadOnly의 'IsAuthenticated' 부분)
        - 비로그인 사용자 접근 시 401 Unauthorized 응답
        """
        # 필수 필드 검증
        required_fields = ['title', 'content', 'product_image']
        for field in required_fields:
            if field not in request.data:
                return Response(
                    {
                        'error': f'{field}은(는) 필수 입력 항목입니다.',
                        'required_fields': required_fields
                    }, 
                    status=status.HTTP_400_BAD_REQUEST
                )

        serializer = ProductDetailSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(author=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ProductDetail(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_object(self, product_pk):
        """상품 객체 가져오기"""
        return get_object_or_404(Product, pk=product_pk)

    def get(self, request, product_pk):
        """상품 상세 조회 API"""
        product = self.get_object(product_pk)
        
        # 작성자가 아닌 경우에만 조회수 증가 (중복 방지)
        if request.user != product.author:
            cache_key = f"view_count_{request.META.get('REMOTE_ADDR')}_{product_pk}"
            if not cache.get(cache_key):
                product.view_count += 1
                product.save()
                # 100초 동안 같은 IP에서 조회수 증가 방지
                cache.set(cache_key, True, 100)
        
        serializer = ProductDetailSerializer(product)   
        return Response(serializer.data)

    def delete(self, request, product_pk):
        """상품 삭제 API"""
        product = self.get_object(product_pk)    
        
        # 작성자 본인만 삭제 가능
        if request.user != product.author:
            return Response({'error': '상품 작성자만 삭제할 수 있습니다.'}, 
                          status=status.HTTP_403_FORBIDDEN)
            
        product.delete()
        return Response({'message': '상품이 삭제되었습니다.'}, 
                      status=status.HTTP_204_NO_CONTENT)

    def put(self, request, product_pk):
        """상품 수정 API"""
        product = self.get_object(product_pk)
        
        # 작성자 본인만 수정 가능
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
        """상품 객체 가져오기"""
        return get_object_or_404(Product, pk=product_pk)

    def get(self, request, product_pk):
        """댓글 목록 조회 API"""
        product = self.get_product(product_pk)
        comments = product.comments.all()
        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data)

    def post(self, request, product_pk):
        """댓글 작성 API"""
        product = self.get_product(product_pk)
        serializer = CommentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(author=request.user, product=product)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CommentLike(APIView):
    def get_comment(self, product, comment_pk):
        """댓글 객체 가져오기"""
        return get_object_or_404(Comment, pk=comment_pk, product=product)

    def post(self, request, product_pk, comment_pk):
        """댓글 좋아요 토글 API"""
        product = get_object_or_404(Product, pk=product_pk)
        comment = self.get_comment(product, comment_pk)
        
        # 이미 좋아요 했으면 취소, 아니면 좋아요 추가
        if comment.like_users.filter(pk=request.user.pk).exists():
            comment.like_users.remove(request.user)
            message = "좋아요 취소"
        else:
            comment.like_users.add(request.user)
            message = "좋아요 완료"

        serializer = CommentSerializer(comment, context={'request': request})
        return Response({
            'message': message,
            'comment': serializer.data
        })


