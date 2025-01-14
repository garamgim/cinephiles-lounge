import requests
from datetime import datetime
from datetime import date
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from .models import *
from .serializers import *
from django.db.models import Q, When, Case, Value
from .utils.load import save_movies, headers
from .utils.recommend_by_likes import recommend_by_likes
from .utils.recommend_by_weather import recommend_by_weather


# 전체 영화 조회
@api_view(['GET'])
def get_movie_list(request):
    if request.method == 'GET':
        movies = Movie.objects.all()
        serializer = MovieSerializer(movies, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


# 영화 순위 5회까지 조회
@api_view(['GET'])
def get_popular(request):
    if request.method == 'GET':
        movies = Movie.objects.all()
        serializer = MovieSerializer(movies[:5], many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


# 장르별 영화 20개 조회
@api_view(['GET'])
def get_genre_movie(request, genre_id):
    if request.method == 'GET':
        movies = Movie.objects.filter(genres__genre_id=genre_id).order_by('?')
        serializer = MovieSerializer(movies[:20], many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


# 최신 개봉작 20개 조회 (개봉일 최신 순으로 정렬)
@api_view(['GET'])
def get_new_release(request):
    if request.method == 'GET':
        movies = Movie.objects.filter(release_date__lte=datetime.now()).order_by('-release_date')
        serializer = MovieSerializer(movies[:20], many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


# 현재 상영작 조회 (3위까지)
@api_view(['GET'])
def get_playing(request):
    if request.method == 'GET':
        page = 1
        processed_count = 0
        now_playing_movies_ids = []

        while processed_count < 3:
            url = 'https://api.themoviedb.org/3/movie/now_playing?language=ko-KR&page=1'
            movie_list = requests.get(url, headers=headers).json().get('results')
            processed_count += save_movies(movie_list)[1]
            for movie_data in movie_list:
                now_playing_movies_ids.append(movie_data.get('id'))
            page += 1

        top_3_movies = Movie.objects.filter(movie_id__in=now_playing_movies_ids).order_by('-popularity')[:3]
        serializer = MovieSerializer(top_3_movies, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)


# 상영 예정작 15개 조회
@api_view(['GET'])
def get_upcoming(request):
    if request.method == 'GET':
        page = 1
        processed_count = 0
        upcoming_movies_ids = []

        while processed_count < 15:
            url = f"https://api.themoviedb.org/3/discover/movie?language=ko-KR&page={page}&sort_by=popularity.desc&primary_release_date.gte={date.today()}"
            movie_list = requests.get(url, headers=headers).json().get('results')
            processed_count += save_movies(movie_list)[1]
            for movie_data in movie_list:
                upcoming_movies_ids.append(movie_data.get('id'))
            page += 1

        upcoming_movies = Movie.objects.filter(movie_id__in=upcoming_movies_ids)
        serializer = MovieSerializer(upcoming_movies, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


# 영화 상세 조회
@api_view(['GET'])
def get_movie_detail(request, movie_id):
    if request.method == 'GET':
        movie = Movie.objects.get(movie_id=movie_id)
        serializer = MovieSerializer(movie)
        return Response(serializer.data, status=status.HTTP_200_OK)


# 영화 좋아요
@permission_classes([IsAuthenticated])
@api_view(['POST'])
def like_movie(request, movie_id):
    if request.method == 'POST':
        movie = Movie.objects.get(movie_id=movie_id)
        
        if movie.liked_users.filter(pk=request.user.pk).exists():
            movie.liked_users.remove(request.user)
        else:
            movie.liked_users.add(request.user)
        
        data = {
            'movie': movie.title,
            'like_count': movie.liked_users.count(),
            'did_i_like': movie.liked_users.filter(pk=request.user.pk).exists()
        }
        return Response(data, status=status.HTTP_200_OK)
        

# 한줄 리뷰 작성
@permission_classes([IsAuthenticated])
@api_view(['POST'])
def create_short_review(request, movie_id):
    if request.method == 'POST':
        movie = Movie.objects.get(movie_id=movie_id)
        serializer = ShortReviewSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save(user=request.user, movie=movie)
            return Response(serializer.data, status=status.HTTP_201_CREATED)


# 한줄 리뷰 수정 / 삭제
@permission_classes([IsAuthenticated])
@api_view(['PUT', 'DELETE'])
def update_short_review(request, short_review_pk):
    short_review = ShortReview.objects.get(pk=short_review_pk)
    if request.user.pk == short_review.user.pk:
        if request.method == 'PUT':
            serializer = ShortReviewSerializer(
                short_review, data=request.data, partial=True
            )
            if serializer.is_valid(raise_exception=True):
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
        elif request.method == 'DELETE':
            short_review.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
    else:
        message = {
            'message': '작성자만 접근이 가능합니다.'
        }
        return Response(message, status=status.HTTP_403_FORBIDDEN)


# 구독하는 사람들이 좋아요 누른 영화 조회
@permission_classes([IsAuthenticated])
@api_view(['GET'])
def get_list_subscribing(request):
    if request.method == 'GET':
        subscriptions = request.user.subscriptions.all()
        subscribing_user_movies = Movie.objects.prefetch_related('liked_users').filter(liked_users__in=subscriptions)
        serializer = MovieSerializer(subscribing_user_movies, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


# 좋아요 기반 추천 알고리즘
@permission_classes([IsAuthenticated])
@api_view(['GET'])
def get_recommendation_like(request):
    if request.method == 'GET':
        liked_movies = request.user.liked_movies.all()
        recommendation_indices = recommend_by_likes(liked_movies)
        recommendation = Movie.objects.filter(id__in=recommendation_indices).exclude(id__in=liked_movies)
        serializer = MovieSerializer(recommendation.order_by('?')[:20], many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    

# 날씨 기반 추천 알고리즘
@permission_classes([IsAuthenticated])
@api_view(['GET'])
def get_recommendation_weather(request):
    if request.method == 'GET':
        lon = request.GET.get('lon')
        lat = request.GET.get('lat')
        api_key = settings.OPEN_WEATHER_API_KEY
        url = f'https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={api_key}'
        weather_id = requests.get(url, headers=headers).json().get('weather')[0].get('id')
        weather_message, result_movie_ids = recommend_by_weather(weather_id)
        recommendation = Movie.objects.filter(movie_id__in=result_movie_ids)
        serializer = MovieSerializer(recommendation, many=True)
        data = {
            'weather_message': weather_message,
            'recommended_movies': serializer.data
        }
        return Response(data, status=status.HTTP_200_OK)


# 제목, 줄거리 기반으로 검색 
# 제목에 검색 키워드를 포함하는 영화를 먼저 반환하고 그다음 줄거리에 키워드를 포함하는 영화들을 반환
@api_view(['GET'])
def get_search(request):
    if request.method == 'GET':
        keyword = request.GET.get('q')
        q1 = Q(title__contains=keyword)
        q2 = Q(overview__contains=keyword)
        results = Movie.objects.filter(q1 | q2).annotate(
          search_order=Case(
              When(q1, then=Value(1)),
              When(q2, then=Value(2)),
            )
        ).order_by('search_order')
        serializer = MovieSerializer(results[:20], many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)



####################################################
################### DB 저장 함수 ###################
####################################################


@permission_classes([IsAdminUser])
@api_view(['POST'])
def set_db(request):
    if request.method == 'POST':
        did_create = False

        for i in range(1, 251):
            url = f'https://api.themoviedb.org/3/discover/movie?include_adult=true&include_video=false&language=ko-KR&page={i}&sort_by=popularity.desc'
            response = requests.get(url, headers=headers).json()
            did_create = save_movies(response.get('results'))[0]

        if did_create:
            return Response(status=status.HTTP_201_CREATED)
        return Response(status=status.HTTP_200_OK)


# 장르 정보 불러오기
# DB에 장르 데이터가 없을때만 저장함
@permission_classes([IsAdminUser])
@api_view(['POST'])
def get_genre(request):
    if request.method == 'POST':
        if not Genre.objects.filter(id=1).exists():
            url = 'https://api.themoviedb.org/3/genre/movie/list?language=ko'
            response = requests.get(url, headers=headers).json()
            
            for genre in response.get('genres'):
                data = {
                    'genre_id': genre.get('id'),
                    'name': genre.get('name')
                }
                
                serializer = GenreSerializer(data=data)

                if serializer.is_valid(raise_exception=True):
                    serializer.save()
                    
            return Response(status=status.HTTP_201_CREATED)
        else:
            message = {
                'message': '장르 데이터가 이미 존재합니다.'
            }
            return Response(data=message)