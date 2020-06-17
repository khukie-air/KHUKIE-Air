
<template>
  <div
    class="index-wrapper"
    :key="current.path"
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
              {{ item.size }} Bytes
            </div>
          </template>

          <!-- 표 내부의 Delete Time 부분 -->
          <template v-slot:item.deleteTime="{ item }">
            <div class="table-column-left">
              {{ item.deleteTime }} Bytes
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
              <!--
              <v-icon
                small
                class="mr-2"
                @click="MoveItem(item)"
              >
                mdi-file-move
              </v-icon>
              <v-icon
                small
                class="mr-2"
                @click="editItem(item)"
              >
                mdi-pencil
              </v-icon>
              <v-icon
                small
                @click="deleteItem(item)"
              >
                mdi-delete
              </v-icon>
              -->
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
    rootFolderID: 0,
    headers: [
      {
        text: 'File Name',
        align: 'start',
        value: 'name'
      },
      { text: 'Size', value: 'size' },
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
      const vm = this
      new Promise(function (resolve, reject) {
        if (vm.current.isRoot) {
          vm.rootFolderID = vm.$store.getters.getUserInfo.rootFolderID
          vm.current.folderID = vm.rootFolderID
          vm.current.path = ''
          vm.current.isRoot = true
        }
        resolve('')
      })
        .then(() => {
          // 아이템
          vm.file = []
          vm.getItems()
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
      const host = this.$store.getters.getHost
      const url = host + '/api/trash/'
      axios.get(url, headers)
        .then((res) => {
          const data = res.data
          // 폴더 먼저 넣기
          data.trashed_items.forEach((element) => {
            if (element.type === 'folder') {
              this.trashes.push({
                name: element.obj_name,
                size: element.size,
                type: 'folder',
                deleteTime: element.trashed_at,
                expireTime: element.expire_time,
                trashID: element.folder_id
              })
            }
          })

          // 파일 나중에 넣기
          data.trashed_items.forEach((element) => {
            if (element.type === 'file') {
              this.trashes.push({
                name: element.obj_name,
                size: element.size,
                type: 'folder',
                deleteTime: element.trashed_at,
                expireTime: element.expire_time,
                trashID: element.folder_id
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
    editItem (item) {
      this.editedIndex = this.file.indexOf(item)
      this.editedItem = Object.assign({}, item)
      this.dialog = true
    },
    deleteItem (item) {
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
      const host = this.$store.getters.getHost
      let url = host
      if (item.type === 'folder') {
        url = url + '/api/folders/' + item.folderID + '/'
      } else {
        url = url + '/api/files/' + item.fileID + '/'
      }

      axios.delete(url, headers)
        .then(() => {
          const index = vm.file.indexOf(item)
          vm.file.splice(index, 1)
        })
        .catch((error) => {
          console.log(error.response)
          if (error.response.status === 401 || error.response.status === 403) {
            alert(error.response.data.message)
          } else if (error.response.status === 404) {
            alert('해당 아이템이 존재하지 않습니다!')
          } else {
            alert('조회 실패!')
          }
        })
    },
    deletePermanently (item) {

    },
    save () {
      // if (this.editedIndex > -1) {
      //   Object.assign(this.file[this.editedIndex], this.editedItem)
      // } else {
      //   this.file.push(this.editedItem)
      // }

      const vm = this

      // 폴더 이름 중복 확인
      let isDuplicated = false
      vm.file.forEach((element) => {
        if (vm.editedItem.name === element.name && element.type === 'folder') {
          isDuplicated = true
        }
      })
      if (isDuplicated) {
        alert('중복된 폴더 이름이 있습니다!')
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
      const params = {
        parent_folder_id: vm.current.folderID,
        folder_name: vm.editedItem.name
      }

      // 요청
      const host = this.$store.getters.getHost
      const url = host + '/api/folders/'
      axios.post(url, params, headers)
        .then((res) => {
          const data = res.data

          vm.file.push({
            name: data.folder_name,
            size: data.size,
            type: 'folder',
            folderID: data.folder_id,
            parentFolderID: data.parent_folder_id,
            path: data.path
          })
        })
        .catch((error) => {
          console.log(error.response)
          if (error.response.status === 401 || error.response.status === 403) {
            alert(error.response.data.message)
          } else {
            alert('폴더 생성 실패!')
          }
        })

      this.close()
    },
    head () {
      return {
        title: '홈페이지'
      }
    }
  }
}
</script>
