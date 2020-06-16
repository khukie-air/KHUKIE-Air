import Vuex from 'vuex'
import axios from 'axios'
// import createPersistedState from 'vuex-persistedstate'

const resourceHost = 'http://khukieair.frec.kr'

const createStore = () => {
  return new Vuex.Store({
    // plugins: [
    //   createPersistedState({
    //     storage: window.sessionStorage
    //   })
    // ],
    state: {
      host: resourceHost,
      accessToken: null,
      refreshToken: null,
      identityId: null,
      accessKeyId: null,
      sessionToken: null,
      secretKey: null,
      userId: null,
      userName: null,
      userEmail: null,
      userSub: null,
      userRootFolderID: null
    },
    getters: {
      getHost: (state) => {
        return state.host
      },
      getAccessToken: (state) => {
        return state.accessToken
      },
      getRefreshToken: (state) => {
        return state.refreshToken
      },
      getUserInfo: (state) => {
        return {
          id: state.userId,
          name: state.userName,
          email: state.userEmail,
          sub: state.userSub,
          rootFolderID: state.userRootFolderID
        }
      },
      getCredentials: (state) => {
        return {
          accessKeyId: state.accessKeyId,
          sessionToken: state.sessionToken,
          secretKey: state.secretKey,
          identityId: state.identityId
        }
      }
    },
    mutations: {
      LOGIN (state, {
        accessToken, refreshToken, identityId, accessKeyId, sessionToken, secretKey, userId, userName, userEmail, userSub, userRootFolderID
      }) {
        state.accessToken = accessToken
        state.refreshToken = refreshToken
        state.identityId = identityId
        state.accessKeyId = accessKeyId
        state.sessionToken = sessionToken
        state.secretKey = secretKey
        state.userId = userId
        state.userName = userName
        state.userEmail = userEmail
        state.userSub = userSub
        state.userRootFolderID = userRootFolderID
      },
      LOGOUT (state) {
        state.accessToken = null
        state.refreshToken = null
        state.identityId = null
        state.accessKeyId = null
        state.sessionToken = null
        state.secretKey = null
        state.userId = null
        state.userName = null
        state.userEmail = null
        state.userSub = null
        state.userRootFolderID = null
      }
    },
    actions: {
      LOGIN ({ commit }, { id, pw }) {
        // Formdata 생성
        const form = new FormData()
        form.append('id', id)
        form.append('pw', pw)

        // Header
        const headers = {
          headers: {
            'Content-Type': 'multipart/form-data'
          }
        }

        // POST 요청
        return axios
          .post(`${resourceHost}/api/auth/login`, form, headers)
          .then((res) => {
            const data = res.data
            console.log('로그인 성공. %s님 환영합니다.', data.User.name)

            // commit LOGIN Action
            commit('LOGIN', {
              accessToken: data.AccessToken,
              refreshToken: data.RefreshToken,
              identityId: data.IdentityId,
              accessKeyId: data.Credentials.AccessKeyId,
              sessionToken: data.Credentials.SessionToken,
              secretKey: data.Credentials.SecretKey,
              userEmail: data.User.email,
              userName: data.User.name,
              userId: data.User.id,
              userSub: data.User.sub,
              userRootFolderID: data.User.root_folder_id
            })
          })
      },
      LOGOUT ({ commit }) {
        commit('LOGOUT')
      }
    }
  })
}

export default createStore
