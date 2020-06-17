
<template>
  <div
    class="index-wrapper"
  >

    <v-card color="brown darken-1" height="760px">

      <!-- 휴지통 표시 -->
      <v-card-title class="headline">
        휴지통
      </v-card-title>

      <!-- 메인 -->
      <v-card-text>

        <!-- 파일 및 폴더 표-->
        <v-data-table
          :headers="headers"
          :items="trashes"
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
              <v-icon
                small
                class="mr-2"
                @click="restoreTrash(item)"
              >
                mdi-backup-restore
              </v-icon>
              <v-icon
                small
                class="mr-2"
                @click="deletePermanently(item)"
              >
                mdi-delete-forever
              </v-icon>
            </div>
          </template>

          <!-- 파일이 없는 경우 표시 -->
          <template v-slot:no-data>
            버린 항목이 존재하지 않습니다!
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
    dialog: false,
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
    trashes: [],
    editedIndex: -1,
    editedItem: {
      name: '',
      size: 0,
      type: 'folder'
    },
    defaultItem: {
      name: '',
      size: 0
    }
  }),
  computed: {
    formTitle () {
      return this.editedIndex === -1 ? 'New Folder' : 'Edit File Name'
    }
  },
  watch: {
    dialog (val) {
      val || this.close()
    },
    current () {
      console.log(this.current)
    }
  },
  created () {
    this.init()
  },
  methods: {
    init () {
      this.trashes = []
      this.getTrashes()
    },
    restoreTrash (item) {
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
      const host = vm.$store.getters.getHost
      const url = host + '/api/trash/' + item.trashID + '/'
      axios.put(url, {}, headers)
        .then(() => {
          alert('성공적으로 복원되었습니다.')
          vm.init()
        })
        .catch((error) => {
          console.log(error.response)
          if (error.response.status === 401 || error.response.status === 403) {
            alert(error.response.data.message)
          } else {
            alert('복원 실패!')
          }
        })
    },
    deletePermanently (item) {
      const vm = this

      // 확인
      const promptResult = prompt('정말 삭제하시려면 "삭제"를 입력해주세요.')
      if (promptResult !== '삭제') {
        alert('잘못 입력하셨습니다.')
        return
      }

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
      const host = vm.$store.getters.getHost
      const url = host + '/api/trash/' + item.trashID + '/'
      axios.delete(url, headers)
        .then(() => {
          alert('성공적으로 삭제되었습니다.')
          vm.init()
        })
        .catch((error) => {
          console.log(error.response)
          if (error.response.status === 401 || error.response.status === 403) {
            alert(error.response.data.message)
          } else {
            alert('삭제 실패!')
          }
        })
    },
    getTrashes () {
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
      const host = vm.$store.getters.getHost
      const url = host + '/api/trash/'
      axios.get(url, headers)
        .then((res) => {
          const data = res.data
          // 폴더 먼저 넣기
          data.trashed_items.forEach((element) => {
            if (element.type === 'folder') {
              vm.trashes.push({
                name: element.obj_name,
                size: element.size,
                type: 'folder',
                deleteTime: element.trashed_at,
                expireTime: element.expire_time,
                trashID: element.trash_id
              })
            }
          })

          // 파일 나중에 넣기
          data.trashed_items.forEach((element) => {
            if (element.type === 'file') {
              vm.trashes.push({
                name: element.obj_name,
                size: element.size,
                type: 'file',
                deleteTime: element.trashed_at,
                expireTime: element.expire_time,
                trashID: element.trash_id
              })
            }
          })
        })
        .catch((error) => {
          console.log(error.response)
          if (error.response.status === 401 || error.response.status === 403) {
            alert(error.response.data.message)
          } else {
            alert('조회 실패!')
          }
        })
    },
    head () {
      return {
        title: '홈페이지'
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
