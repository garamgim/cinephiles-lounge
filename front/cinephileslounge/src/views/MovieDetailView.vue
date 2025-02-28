<template>
  <div class="detail-view">
    <div class="detail-container">
      <div class="movie-content">
        <div class="content-title">
          <h2>{{ movieStore.movie.title }}</h2>
          <div class="content-des">
            <span v-if="movieStore.movie.vote_average">
              <i class="bx bxs-star"></i>
              {{ movieStore.movie.vote_average.toFixed(1) }}
            </span>
            <span>{{ movieStore.movie.release_date }}</span>
            <span>{{ genres }}</span>
          </div>
        </div>
        <div class="content-overview">
          <p>{{ truncateOverview(movieStore.movie.overview, 400) }}</p>
        </div>
        <div class="content-btn">
          <i v-if="!isLiked" @click="movie_like" class="bx bx-heart"></i>
          <i v-if="isLiked" @click="movie_like" class="bx bxs-heart"></i>
          <div @click="navigateToCreateArticle" class="article-btn">
            <i class="bx bx-plus"></i>
            <span>게시글 작성</span>
          </div>
        </div>
      </div>

      <div class="movie-video">
        <iframe
          v-if="movieStore.movie.trailer_key"
          :src="`https://www.youtube.com/embed/${movieStore.movie.trailer_key}?autoplay=1&controls=0&loop=1&playlist=${movieStore.movie.trailer_key}&mute=1`"
          allow="autoplay"
        ></iframe>
      </div>
    </div>
    <div class="review-container">
      <h1>시네필라운지 한줄평</h1>

      <MovieDetailList
        :shortReviews="movieStore.movie.shortreview_set"
        :movieId="movieStore.movie.movie_id"
      />
    </div>
  </div>
</template>
<script setup>
import { ref, computed, onMounted, onUnmounted } from "vue";
import {
  useRoute,
  useRouter,
  onBeforeRouteUpdate,
  onBeforeRouteLeave,
} from "vue-router";
import { useMovieStore } from "@/stores/movie";
import { useAccountStore } from "@/stores/account";
import { useFeedStore } from "@/stores/feed";
import MovieDetailList from "@/components/MovieDetailList.vue";
import axios from "axios";
const movieStore = useMovieStore();
const accountStore = useAccountStore();
const feedStore = useFeedStore();
const route = useRoute();
const router = useRouter();
const movieId = ref(route.params.movie_id);

movieStore.getMovieDetail(movieId.value);

const reviews = ref();
const genres = ref();
onMounted(() => {
  genres.value = movieStore.movie.genres.map((item) => item.name).join(" · "); // 장르 이름만 뽑아서 공백으로 구분
});
onUnmounted(() => {
  movieStore.movie.trailer_key = "";
});
// 줄거리가 길면 400글자에서 자르기
const truncateOverview = (overview, maxLength) => {
  return overview.length > maxLength
    ? overview.substring(0, maxLength) + "..."
    : overview;
};

// 좋아요 눌렀는지 확인
const isLiked = computed(() => {
  if (!movieStore.movie.liked_users) return false; // 좋아요 누른 유저가 아무도 없으면 false
  return movieStore.movie.liked_users.some(
    // 현재 유저가 좋아요 눌렀으면 true
    (user) => user.id === accountStore.userPk
  );
});

// 영화 좋아요
const movie_like = () => {
  axios({
    method: "post",
    url: `${accountStore.API_URL}/movies/${movieStore.movie.movie_id}/like/`,
    headers: {
      Authorization: `Token ${accountStore.token}`,
    },
  })
    .then((res) => {
      console.log("좋아요 성공");
      if (movieStore.movie.liked_users) {
        const userIndex = movieStore.movie.liked_users.findIndex(
          (user) => user.id === accountStore.userPk
        );
        if (userIndex > -1) {
          movieStore.movie.liked_users.splice(userIndex, 1);
        } else {
          movieStore.movie.liked_users.push({
            id: accountStore.userPk,
            username: accountStore.username,
          });
        }
      }
    })
    .catch((err) => {
      console.log(err);
    });
};

// 게시글 작성 페이지로 이동
const navigateToCreateArticle = () => {
  feedStore.articleCreateId = movieId.value;
  feedStore.articleMovieImg = movieStore.movie.backdrop_path;
  feedStore.articleMovieTitle = movieStore.movie.title;
  feedStore.articleMovieOverview = movieStore.movie.overview;
  router.push({ name: "FeedCreateView" });
};
</script>
<style scoped>
.detail-view {
  padding-top: 50px;
  width: 100vw;
  min-height: 100vh;
  background-color: black;
  color: #fff;
  display: flex;
  flex-direction: column;
}
.detail-container {
  position: relative;
  height: 431px;
  margin-bottom: 20px;
  display: flex;
  flex-direction: column;
  margin-left: 200px;
}
.detail-container .movie-content {
  margin-top: 72px;
  position: relative;
  width: 100%;
  height: 359px;
  display: flex;
  flex-direction: column;
}
.detail-container .movie-img img {
  border-radius: 5px;
}
.detail-container .movie-video {
  position: absolute;
  top: 0px;
  bottom: 22px;
  left: 680px;
  width: 950px;
}
.detail-container .movie-video iframe {
  width: 800px;
  height: 405px;
  display: inline;
}
.detail-container .movie-content .content-title {
  width: 100%;
  height: 96px;
  display: flex;
  flex-direction: column;
  align-items: flex-start;
}
.detail-container .movie-content .content-title h2 {
  font-size: 40px;
  font-weight: 700;
  height: 50px;
}
.detail-container .movie-content .content-title .content-des {
  font-size: 15px;
  line-height: 1.33em;
  width: 334px;
  margin-top: 10px;
}
.detail-container .movie-content .content-title .content-des span {
  font-size: 15px;
  line-height: 1.5em;
  padding: 1px 5px;
  width: 22px;
  height: 20px;
  margin-right: 10px;
  color: #babac1;
}
.detail-container .movie-content .content-overview {
  width: 100%;
  padding-bottom: 10px;
}
.detail-container .movie-content .content-overview p {
  font-size: 16px;
  line-height: 25px;
  width: 600px;
  max-width: 700px;
  color: #84868d;
}
.detail-container .movie-content .content-btn {
  margin-top: 8px;
  width: 100%;
  display: flex;
  align-items: center;
  color: #84868d;
}
.detail-container .movie-content .content-btn .article-btn {
  display: flex;
  margin-left: 500px;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  transition: 0.3s;
  cursor: pointer;
}
.detail-container .movie-content .content-btn .article-btn:hover {
  transform: scale(1.1);
  color: #eee;
}
.detail-container .movie-content .content-btn i {
  font-size: 30px;
  cursor: pointer;
}
.detail-container .movie-content .content-btn .bx-heart {
  color: #908c93;
  transition: 0.3s;
}
.detail-container .movie-content .content-btn .bx-heart:hover {
  transform: scale(1.1);
  color: #eee;
}
.detail-container .movie-content .content-btn .bxs-heart {
  color: #f82e62;
  transition: 0.3s;
}
.detail-container .movie-content .content-btn .bxs-heart:hover {
  transform: scale(1.1);
}

.review-container {
  margin-left: 200px;
}
.review-container h1 {
  font-size: 20px;
  font-weight: 700;
  line-height: 1.3em;
  letter-spacing: 2px;
}
</style>
