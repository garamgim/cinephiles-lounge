<template>
  <main>
    <div class="sign-in-container">
      <div class="title-wrapper">
        <span>로그인</span>
        <a href="#">비밀번호를 잊어버리셨나요?</a>
      </div>
      <form @submit.prevent="logIn" class="sign-in-form">
        <div class="username-box">
          <input
            @input="validateUsername"
            
            class="username-wrapper"
            type="text"
            placeholder="아이디"
          />
          <i v-if="showUsernameIcon && !usernameSuccess" class="bx bxs-x-circle"></i>
          <i
            v-if="showUsernameIcon && usernameSuccess"
            class="bx bxs-chevron-down-circle"
          ></i>
        </div>
        <div class="pwd-box">
          <input
            @input="validatePwd"
            class="pwd-wrapper"
            type="password"
            placeholder="비밀번호"
          />
          <i v-if="showPwdIcon && !pwdSuccess" class="bx bxs-x-circle"></i>
          <i
            v-if="showPwdIcon && pwdSuccess"
            class="bx bxs-chevron-down-circle"
          ></i>
        </div>
        <div class="login-btn-wrapper">
          <button
            :disabled="!buttonActive"
            :style="{ opacity: buttonActive ? '1' : '0.3' }"
          >
            로그인
          </button>
        </div>
      </form>
      <p class="another-login">다른 방법으로 로그인하기</p>
      <ul>
        <li></li>
        <li></li>
        <li></li>
        <li></li>
        <li></li>
      </ul>
    </div>
  </main>
</template>

<script setup>
// 더 해야할거 : form제출 이벤트막고 다른 함수 넣기, 비밀번호 찾기 기능, 소셜로그인, icon이랑 link넣기

import { ref, computed } from "vue";
import {useAccountStore} from '@/stores/account.js'
const username = ref("");
const password = ref("");
const usernameSuccess = ref(false);
const showUsernameIcon = ref(false);
const pwdSuccess = ref(false);
const showPwdIcon = ref(false);
const accountStore = useAccountStore()

// 로그인
const logIn = ()=>{
  const payload = {
    username:username.value,
    password:password.value,
  }
  accountStore.logIn(payload)
}

// 유저네임 입력 시작 -> failed icon -> show
// 유저네임 5글자 이상 입력 -> failed icon hide && success icon show
// 5 <= 유저네임 <= 15, 영어, 숫자만 가능
const validateUsername = (e) => {
  username.value = e.target.value;
  if (username.value.length > 0) {
    showUsernameIcon.value = true; //입력이 있을때만 아이콘 표시
    // usernameSuccess.value = username.value.includes("@") && username.value.includes(".");
    usernameSuccess.value = (5<= username.value.length && username.value.length <= 15 && /^[a-zA-Z0-9]+$/.test(username.value))  
    // 이메일형식 @, dot이 있을때만 success아이콘 표시
  } else {
    showUsernameIcon.value = false;
  }
};

// 비밀번호 입력 시작 -> failed icon show
// 비밀번호 8자리 이상 입력 -> failed icon hide && success icon show
const validatePwd = (e) => {
  password.value = e.target.value;
  if (password.value.length > 0) {
    showPwdIcon.value = true; //입력이 있을때만 아이콘 표시
    pwdSuccess.value = password.value.length >= 8;
  } else {
    showPwdIcon.value = false;
  }
};

// 이메일, 비밀번호 모두 형식에 맞으면 로그인 버튼 활성화
const buttonActive = computed(() => {
  return usernameSuccess.value && pwdSuccess.value;
});
</script>

<style scoped>
main {
  display: flex;
  justify-content: center;
  align-items: center;
  width: 100vw;
  height: 100vh;
  background-image: url("../assets/loginBackground.webp");
}

.sign-in-container {
  margin-top: 50px;
  width: 300px;
  height: 293.5px;
}

.sign-in-container .title-wrapper {
  display: flex;
  justify-content: space-between;
}
.sign-in-container div span {
  font-size: 20px;
  color: #fff;
}

.sign-in-container div a {
  font-size: 12px;
  padding-top: 4px;
  text-decoration: none;
  color: #6f7073;
}

.sign-in-container div a:hover {
  text-decoration: underline;
}

.sign-in-container .sign-in-form {
  margin-top: 16px;
}

.sign-in-container .sign-in-form .username-box {
  position: relative;
}
.sign-in-container .sign-in-form .pwd-box {
  position: relative;
}

.sign-in-container .sign-in-form .bxs-x-circle {
  color: #db4241;
  position: absolute;
  right: 10px;
  top: 10px;
  font-size: 20px;
  pointer-events: none;
}

.sign-in-container .sign-in-form .bxs-chevron-down-circle {
  color: #3daaff;
  position: absolute;
  right: 10px;
  top: 10px;
  font-size: 20px;
  pointer-events: none;
}

.sign-in-container .sign-in-form .login-btn-wrapper {
  margin-top: 16px;
  padding-bottom: 21px;
  border-bottom: 1px solid #27262d;
}

.sign-in-container .sign-in-form .login-btn-wrapper button {
  width: 300px;
  height: 48px;
  margin-bottom: 1px;
  border: none;
  color: #fff;
  background-color: rgb(248, 47, 98);
  border-radius: 30px;
  font-weight: 700;
  line-height: 47px;
}
.sign-in-container .sign-in-form div input {
  padding: 10px 10px 10px 14px;
  font-size: 16px;
  width: 274px;
  border: none;
  outline: none;
}

.sign-in-container .sign-in-form .username-wrapper {
  border-bottom: 1px solid #ebeaec;
  border-top-left-radius: 5px;
  border-top-right-radius: 5px;
}
.sign-in-container .sign-in-form .pwd-wrapper {
  border-bottom-left-radius: 5px;
  border-bottom-right-radius: 5px;
}
.sign-in-container .another-login {
  margin-top: 15px;
  margin-bottom: 13px;
  font-size: 12px;
  color: #6f7073;
}
</style>
