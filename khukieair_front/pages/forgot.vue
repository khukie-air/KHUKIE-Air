<template>
  <div class="container">
    <div class="signform">
      <h2>비밀번호를 잊으셨나요?</h2>
      <p>
        비밀번호를 재설정하려면 이메일 주소를 입력하세요. <br>
        이메일을 받지 못한 경우 스팸함을 살펴보세요.
      </p>
      <form action="" method="POST">
        <input type="text" name="email" placeholder="E-mail">
        <br>
        <btn type="submit">
          보내기
        </btn>
      </form>
    </div>
    <div class="signform-help">
      <a href="/signin">기존 계정으로 로그인</a>
    </div>
    <div class="warning">
      test msg!!
    </div>
  </div>
</template>
