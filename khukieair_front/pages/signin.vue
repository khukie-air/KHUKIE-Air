<template>
  <div class="container">
    <div class="signform">
      <h2>Sign in to KHUKIE</h2>
      <form action="" method="POST">
        <input type="text" name="email" placeholder="E-mail">
        <br>
        <input type="password" name="password" placeholder="Password">
        <br>
        <btn type="submit">
          로그인
        </btn>
      </form>
    </div>
    <div class="signform-help">
      <a href="/forgot">비밀번호를 잊으셨나요?</a>
      &nbsp;•&nbsp;
      <a href="/signup">계정 만들기</a>
    </div>
    <div class="line" />
    <div class="OAuth">
      <btn type="button" onclick="">
        <img src="~/assets/google.png">
        구글 계정으로 로그인
      </btn>
      <btn type="button" onclick="">
        <img src="~/assets/kakao.png">
        카카오 계정으로 로그인
      </btn>
    </div>
  </div>
</template>
