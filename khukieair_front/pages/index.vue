<template>
  <div>
    <p> [임시 페이지] </p>
    <p>
      <nuxtLink to="/">
        임시 페이지로
      </nuxtLink>
    </p>
    <br>
    <p>
      <nuxtLink to="/signin">
        signin (기존 시작 페이지, auth X)
      </nuxtLink>
    </p>
    <p>
      <nuxtLink to="/signup">
        signup
      </nuxtLink>
    </p>
    <p>
      <nuxtLink to="/forgot">
        forgot
      </nuxtLink>
    </p>
    <br>
    <div> [Home Page of khukie-air] </div>
    <p>
      <nuxtLink to="/home">
        유저 홈 페이지 (로그인 시 홈페이지, auth O)
      </nuxtLink>
    </p>
  </div>
</template>
