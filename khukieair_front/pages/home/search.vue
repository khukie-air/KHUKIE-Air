
<template>
  <div
    class="index-wrapper"
  >

    <v-card color="brown darken-1" height="760px">

      <!-- 검색 결과 표시 -->
      <v-card-title class="headline">
        "{{ query }}" 검색 결과
      </v-card-title>

      <!-- 메인 -->
      <v-card-text>

        <!-- 파일 및 폴더 표-->
        <v-data-table
          :headers="headers"
          :items="results"
          @click:row="getIntoFolder"
          sort-by="name"
          class="elevation-1 brown"
        >

          <!-- 표 내부의 File Name 부분 -->
          <template v-slot:item.name="{ item }">
            <div
              class="table-column-left"
            >
              <v-icon
                small
                class="mr-2"
              >mdi-{{ (item.type === 'folder') ? 'folder' : 'paperclip' }}</v-icon>
              {{ item.name }}
            </div>
          </template>

          <!-- 표 내부의 Size 부분 -->
          <template v-slot:item.size="{ item }">
            <div class="table-column-left">
              {{ convertSize(item.size) }}
            </div>
          </template>

          <!-- 표 내부의 Delete Time 부분 -->
          <template v-slot:item.deleteTime="{ item }">
            <div class="table-column-left">
              {{ item.deleteTime }}
            </div>
          </template>

          <!-- 표 내부의 수정부-->
          <template v-slot:item.actions="{ item }">
            <div class="table-column-left">

              <!-- 다운로드 Action -->
              <v-tooltip bottom>
                <template v-slot:activator="{ on, attrs }">
                  <v-icon
                    small
                    class="mr-2"
                    v-bind="attrs"
                    v-on="on"
                    :disabled="item.type === 'folder'"
                    @click="downLoadItem(item)"
                  >
                    mdi-download
                  </v-icon>
                </template>
                <span>파일 다운로드</span>
              </v-tooltip>

            </div>
          </template>

          <!-- 파일이 없는 경우 표시 -->
          <template v-slot:no-data>
            검색 결과가 존재하지 않습니다!
            <v-btn color="brown darken-4" @click="init">
              Reset
            </v-btn>
          </template>

        </v-data-table>
        <!-- 하단 잡글 -->
        <hr class="my-1">
        <div class="text-xs-right">
          <em>Everyone loves khukie :D <small>&mdash; Khukie Monster</small></em>
        </div>
      </v-card-text>
    </v-card>
  </div>
</template>

<script>
import axios from 'axios'
export default {
  layout: 'homeLayout',
  data: () => ({
    query: '',
    headers: [
      {
        text: 'File Name',
        align: 'start',
        value: 'name'
      },
      { text: 'Size', value: 'size' },
      { text: 'Deleted Time', value: 'deleteTime' },
      { text: 'Actions', value: 'actions', sortable: false }
    ],
    results: []
  }),
  created () {
    this.results = []
    this.getResults()
  },
  methods: {
    getResults () {
      const vm = this

      // Query
      const query = decodeURI(this.$route.query.query)
      this.query = query

      // Header
      const creds = vm.$store.getters.getCredentials
      const headers = {
        headers: {
          Authorization: vm.$store.getters.getAccessToken,
          'X-Identity-Id': creds.identityId,
          'X-Cred-Access-Key-Id': creds.accessKeyId,
          'X-Cred-Session-Token': creds.sessionToken,
          'X-Cred-Secret-Access-Key': creds.secretKey,
          'Content-Type': 'application/json'
        }
      }
      const params = { query }

      // 요청
      const host = vm.$store.getters.getHost
      const url = host + '/api/search/'
      axios.post(url, params, headers)
        .then((res) => {
          const data = res.data
          // 폴더 먼저 넣기
          data.items.forEach((element) => {
            if (element.type === 'folder') {
              vm.results.push({
                name: element.folder_name,
                size: element.size,
                type: 'folder',
                folderID: element.folder_id
              })
            }
          })

          // 파일 나중에 넣기
          data.items.forEach((element) => {
            if (element.type === 'file') {
              vm.results.push({
                name: element.file_name,
                size: element.size,
                type: 'file',
                fileID: element.file_id
              })
            }
          })
        })
        .catch((error) => {
          console.log(error.response)
          if (error.response.status === 401 || error.response.status === 403) {
            alert(error.response.data.message)
          } else {
            alert('검색 실패!')
          }
        })
    },
    downLoadItem (item) {
      const vm = this

      // Header
      const creds = vm.$store.getters.getCredentials
      const headers = {
        headers: {
          Authorization: vm.$store.getters.getAccessToken,
          'X-Identity-Id': creds.identityId,
          'X-Cred-Access-Key-Id': creds.accessKeyId,
          'X-Cred-Session-Token': creds.sessionToken,
          'X-Cred-Secret-Access-Key': creds.secretKey,
          'Content-Type': 'application/json'
        }
      }

      // 요청
      const host = this.$store.getters.getHost
      const url = host + '/api/files/' + item.fileID + '/'
      axios.get(url, headers)
        .then((res) => {
          const downloadURL = res.data

          let filename = downloadURL.split('?')[0].split('/')
          filename = decodeURI(filename[filename.length - 1])
          vm.fileDownload(downloadURL, 'GET', filename)
        })
        .catch((error) => {
          console.log(error.response)
          if (error.response.status === 401 || error.response.status === 403) {
            alert(error.response.data.message)
          } else {
            alert('파일 다운로드 실패!')
          }
        })
    },
    async fileDownload (url, method, fileName) {
      const axiosConfig = {
        method,
        url,
        responseType: 'blob'
      }

      try {
        const response = await axios(axiosConfig)

        const url = window.URL.createObjectURL(new Blob([response.data]))
        const anchor = document.createElement('a')

        anchor.href = url
        anchor.setAttribute('download', fileName)
        document.body.appendChild(anchor)
        anchor.click()
      } catch (err) {
        alert('파일 다운로드 중 에러가 발생했습니다. ' + err)
      }
    },
    convertSize (origin) {
      let text = 'Bytes'
      let size = origin
      if (size >= 1024) {
        size = (size / 1024).toFixed(2)
        text = 'KB'
      }
      if (size >= 1024) {
        size = (size / 1024).toFixed(2)
        text = 'MB'
      }
      if (size >= 1024) {
        size = (size / 1024).toFixed(2)
        text = 'GB'
      }
      return size + ' ' + text
    }
  }
}
</script>
