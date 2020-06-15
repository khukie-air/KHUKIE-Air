<template>
  <div class="container">
    <div class="signform">
      <h2>Sign up to KHUKIE</h2>
      <form action="" method="POST">
        <input type="text" name="firstname" placeholder="First name">
        <br>
        <input type="text" name="lastname" placeholder="Last name">
        <br>
        <input type="text" name="email" placeholder="E-mail">
        <br>
        <input type="password" name="password" placeholder="Password">
        <br>
        <btn type="submit">
          가입
        </btn>
      </form>
    </div>
    <div class="signform-help">
      <a href="/signin">기존 계정으로 로그인</a>
    </div>
    <div class="warning">
      test msg!!
    </div>
    <div class="line" />
    <div class="OAuth">
      <btn type="button" onclick="">
        <img src="~/assets/google.png">
        구글 계정으로 가입
      </btn>
      <btn type="button" onclick="">
        <img src="~/assets/kakao.png">
        카카오 계정으로 가입
      </btn>
    </div>
  </div>
</template>
