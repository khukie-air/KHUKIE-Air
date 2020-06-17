<template>
  <div
    class="index-wrapper"
    :key="current.path"
  >

    <v-card color="brown darken-1" height="760px">

      <!-- 현재 디렉토리 표시 -->
      <v-card-title class="headline">
        /{{ current.path }}
      </v-card-title>

      <!-- 메인 -->
      <v-card-text>

        <!-- 근데여기서 search는 폴더 내에 있는 거는 못볼텐데... 의미 없는듯, search는 따로 만들어야 될듯 -->
        <v-text-field
          v-model="search"
          solo-inverted
          hide-details
          label="Search"
        />

        <!-- 파일 및 폴더 표-->
        <v-data-table
          :headers="headers"
          :items="file"
          :search="search"
          sort-by="name"
          class="elevation-1 brown"
        >
          <!-- 상단부 -->
          <template v-slot:top>
            <v-toolbar flat color="brown darken-2">

              <!-- 루트폴더 버튼 -->
              <v-btn
                color="brown darken-3"
                class="mb-2"
                @click="getIntoRootFolder"
              >
                <v-icon>mdi-home</v-icon>
              </v-btn>

              &nbsp;

              <!-- 상위폴더 버튼 -->
              <v-btn
                color="brown darken-3"
                class="mb-2"
                @click="getIntoParentFolder"
                :disabled="current.isRoot"
              >
                <v-icon>mdi-arrow-up</v-icon>
              </v-btn>

              &nbsp;

              <!-- 새로고침버튼 -->
              <v-btn
                color="brown darken-3"
                class="mb-2"
                @click="init"
              >
                <v-icon>mdi-refresh</v-icon>
              </v-btn>

              <v-spacer />

              <!-- 폴더 생성 버튼 및 모달 -->
              <v-dialog v-model="dialog" max-width="500px">
                <template v-slot:activator="{ on, attrs }">
                  <v-btn
                    color="brown darken-3"
                    class="mb-2"
                    v-bind="attrs"
                    v-on="on"
                  >
                    <v-icon left>
                      mdi-folder-plus
                    </v-icon>
                    New Folder
                  </v-btn>
                </template>

                <!-- 버튼 클릭 후 새 창-->
                <v-card color="brown">
                  <v-card-title>
                    <span class="headline">{{ formTitle }}</span>
                  </v-card-title>
                  <v-card-text>
                    <v-container>
                      <v-row>
                        <v-col cols="12" sm="6" md="4">
                          <v-text-field v-model="editedItem.name" label="Folder name" />
                        </v-col>
                      </v-row>
                    </v-container>
                  </v-card-text>

                  <!-- 내부 버튼 -->
                  <v-card-actions>
                    <v-spacer />
                    <v-btn color="brown darken-3" text @click="close">
                      Cancel
                    </v-btn>
                    <v-btn color="brown darken-3" text @click="save">
                      Save
                    </v-btn>
                  </v-card-actions>
                </v-card>
              </v-dialog>

              &nbsp;

              <!-- 파일 업로드 버튼 및 모달 -->
              <v-dialog v-model="fileDialog" max-width="500px">
                <template v-slot:activator="{ on, attrs }">
                  <v-btn
                    color="brown darken-3"
                    class="mb-2"
                    v-bind="attrs"
                    v-on="on"
                  >
                    <v-icon left>
                      mdi-file-upload
                    </v-icon>
                    File Upload
                  </v-btn>
                </template>

                <!-- 버튼 클릭 후 새 창-->
                <v-card color="brown">
                  <v-card-title>
                    <span class="headline">{{ formTitle }}</span>
                  </v-card-title>
                  <v-card-text>
                    <v-container>
                      <v-row>
                        <v-col cols="12" sm="6" md="4">
                          <v-file-input
                            small-chips
                            v-model="fileInput"
                            label="File Upload"
                            refs="fileInput"
                          /> <!-- 파일 인풋-->
                        </v-col>
                      </v-row>
                    </v-container>
                  </v-card-text>

                  <!-- 내부 버튼 -->
                  <v-card-actions>
                    <v-spacer />
                    <v-btn color="brown darken-3" text @click="closeFileModal">
                      Cancel
                    </v-btn>
                    <v-btn color="brown darken-3" text @click="fileUpload">
                      Upload
                    </v-btn>
                  </v-card-actions>
                </v-card>
              </v-dialog>
            </v-toolbar>
          </template>

          <!-- 표 내부의 File Name 부분 -->
          <template v-slot:item.name="{ item }">
            <div
              class="table-column-left"
              :style="{ cursor: ((item.type === 'folder') ? 'pointer' : 'default') }"
            >
              <v-btn
                dense
                text
                small
                @click="getIntoFolder(item)"
              >
                <v-icon
                  small
                  class="mr-2"
                >mdi-{{ (item.type === 'folder') ? 'folder' : 'paperclip' }}</v-icon>
                {{ item.name }}
              </v-btn>
            </div>
          </template>

          <!-- 표 내부의 Size 부분 -->
          <template v-slot:item.size="{ item }">
            <div class="table-column-left">
              {{ item.size }} Bytes
            </div>
          </template>

          <!-- 표 내부의 수정부-->
          <template v-slot:item.actions="{ item }">
            <div class="table-column-left">
              <v-icon
                small
                class="mr-2"
                :disabled="item.type === 'folder'"
                @click="HashItem(item)"
              >
                mdi-pound
              </v-icon>
              <v-icon
                small
                class="mr-2"
                :disabled="item.type === 'folder'"
                @click="downLoadItem(item)"
              >
                mdi-download
              </v-icon>
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
            </div>
          </template>

          <!-- 파일이 없는 경우 표시 -->
          <template v-slot:no-data>
            항목이 존재하지 않습니다!
            <br>
            새로고침 해보시거나 새로운 폴더 및 파일을 업로드해주세요.
            <br>
            <v-btn color="brown darken-4" @click="init">
              Load
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
    fileDialog: false,
    search: null,
    rootFolderID: 0,
    current: {
      path: '',
      folderID: 0,
      parentFolderID: 0,
      isRoot: true
    },
    headers: [
      {
        text: 'File Name',
        align: 'start',
        value: 'name'
      },
      { text: 'Size', value: 'size' },
      { text: 'Actions', value: 'actions', sortable: false }
    ],
    file: [],
    editedIndex: -1,
    editedItem: {
      name: '',
      size: 0,
      type: 'folder',
      id: 0
    },
    fileInput: null,
    defaultItem: {
      name: '',
      size: 0
    }
  }),
  computed: {
    formTitle () {
      return this.editedIndex === -1 ? 'New Folder' : 'Edit Name'
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
    getItems () {
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
      const url = host + '/api/folders/' + this.current.folderID + '/items/'
      axios.get(url, headers)
        .then((res) => {
          const data = res.data
          // 폴더 먼저 넣기
          data.items.forEach((element) => {
            if (element.type === 'folder') {
              this.file.push({
                name: element.folder_name,
                size: element.size,
                type: 'folder',
                folderID: element.folder_id,
                parentFolderID: element.parent_folder_id,
                path: element.path
              })
            }
          })

          // 파일 나중에 넣기
          data.items.forEach((element) => {
            if (element.type === 'file') {
              this.file.push({
                name: element.file_name,
                size: element.size,
                type: 'file',
                fileID: element.file_id,
                parentFolderID: element.parent_folder_id,
                path: element.path
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
    editItem (item) {
      this.editedIndex = this.file.indexOf(item)
      this.editedItem = Object.assign({}, item)
      console.log(this.editedItem)
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
    close () {
      this.dialog = false
      this.$nextTick(() => {
        this.editedItem = Object.assign({}, this.defaultItem)
        this.editedIndex = -1
      })
    },
    save () {
      const vm = this

      // 폴더 및 파일 이름 변경
      if (vm.editedIndex > -1) {
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

        // 바꾸려는 이름이 존재하는지 확인
        let isDuplicated = false
        vm.file.forEach((element) => {
          if (element.name === vm.editedItem.name) {
            alert('폴더 내에 동일한 이름이 있습니다.')
            isDuplicated = true
          }
        })
        if (isDuplicated) {
          vm.close()
          return
        }

        // Parameters & url
        const host = this.$store.getters.getHost
        let params
        let url = host
        if (vm.editedItem.type !== 'folder') {
          params = {
            new_name: vm.editedItem.name
          }
          url = url + '/api/files/' + vm.editedItem.fileID + '/name/'
        } else {
          params = {
            new_folder_name: vm.editedItem.name
          }
          url = url + '/api/folders/' + vm.editedItem.folderID + '/name/'
        }

        // 요청
        axios.put(url, params, headers)
          .then(() => {
            alert('성공적으로 변경되었습니다.')
            vm.init()
          })
          .catch((error) => {
            console.log(error.response)
            if (error.response.status === 401 || error.response.status === 403) {
              alert(error.response.data.message)
            } else {
              alert('변경 실패!')
            }
          })
      } else {
        // 폴더 생성

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
      }

      this.close()
    },
    head () {
      return {
        title: '홈페이지'
      }
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
    getIntoRootFolder () {
      const vm = this
      vm.getIntoFolder({
        path: '',
        folderID: vm.rootFolderID,
        parentFolderID: vm.rootFolderID
      })
    },
    getIntoParentFolder () {
      const vm = this

      if (!this.current.isRoot) {
        vm.getFolderInfo(vm.current.parentFolderID)
          .then((folder) => {
            vm.getIntoFolder(folder)
          })
      }
    },
    getIntoFolder (item) {
      if (item.type === 'file') {
        return
      }

      const vm = this

      new Promise(function (resolve, reject) {
        vm.current.path = item.path
        vm.current.folderID = item.folderID
        vm.current.parentFolderID = item.parentFolderID
        vm.current.isRoot = (vm.rootFolderID === item.folderID)
        resolve()
      })
        .then(() => {
          vm.init()
        })
    },
    getFolderInfo (folderID) {
      // 폴더의 정보를 가져옴
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
      const url = host + '/api/folders/' + folderID + '/'
      return axios.get(url, headers)
        .then((res) => {
          const data = res.data
          return Promise.resolve({
            type: 'folder',
            folderID: data.folder_id,
            parentFolderID: data.parentFolderID,
            path: data.path,
            name: data.folder_name,
            size: data.size
          })
        })
        .catch((error) => {
          console.log(error.response)
          if (error.response.status === 401 || error.response.status === 403) {
            alert(error.response.data.message)
          } else {
            alert('폴더 데이터 조회 실패!')
          }
        })
    },
    fileUpload () {
      if (this.fileInput === null) {
        alert('파일을 선택해주세요.')
        return
      }
      const targetFile = this.fileInput

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
      const params = {
        attributes: {
          file_name: targetFile.name,
          size: targetFile.size,
          content_created_at: targetFile.lastModifiedDate,
          content_modified_at: targetFile.lastModifiedDate,
          loc_folder_id: vm.current.folderID
        }
      }

      // 요청
      const host = this.$store.getters.getHost
      const url = host + '/api/files/'
      axios.post(url, params, headers)
        .then((res) => {
          const data = res.data
          const uploadURL = data.url
          const fields = data.fields

          const form = new FormData()
          Object.keys(fields).forEach((key) => {
            form.append(key, fields[key])
          })
          form.append('file', targetFile)

          const xhr = new XMLHttpRequest()
          xhr.open('POST', uploadURL, true)
          xhr.send(form)
          xhr.onload = function () {
            if (this.status === 204) {
              alert('업로드 성공!')
              vm.closeFileModal()
              vm.init()
            } else {
              console.log(this.responseText)
              alert('업로드 실패!')
            }
          }
        })
        .catch((error) => {
          console.log(error)
          alert('실패!')
        })
    },
    closeFileModal () {
      this.fileDialog = false
    }
  }
}
</script>
