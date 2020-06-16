<template>
  <div class="container">
    <div class="signform">
      <h2>비밀번호를 잊으셨나요?</h2>
      <p>
        비밀번호를 재설정하려면 가입한 ID를 입력하세요. <br>
        이메일을 받지 못한 경우 스팸함을 살펴보세요.
      </p>
      <div class="signform-inner">
        <input v-model="id" type="text" name="id" placeholder="id" @keyup.enter="reqFindPW">
        <br>
        <button @click="reqFindPW">
          보내기
        </button>
      </div>
    </div>
    <div class="signform-help">
      <a href="/signin">기존 계정으로 로그인</a>
    </div>
  </div>
</template>

<script>
import axios from 'axios'

export default {
  data: () => {
    return {
      id: null
    }
  },
  methods: {
    reqFindPW () {
      if (this.id === '' || this.id === null) {
        alert('이메일을 입력해주세요.')
        return
      }

      const vm = this

      // Formdata 생성
      const form = new FormData()
      form.append('id', this.id.toLowerCase())

      // Header
      const headers = {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      }

      // POST 요청
      const host = this.$store.getters.getHost
      const url = host + '/api/auth/findpw'
      axios.post(url, form, headers)
        .then((res) => {
          alert('기입하신 메일로 인증번호가 발송되었습니다.')
          vm.$router.push('/resetpw')
        })
        .catch((error) => {
          console.log(error.response)
          if (error.response.status === 400) {
            alert(error.response.data.message)
          } else {
            alert('에러 발생!')
          }
        })
    }
  }
}
</script>
