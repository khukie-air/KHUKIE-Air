<template>
  <v-card color="brown darken-1" height="760px">
    <v-card-title class="headline">
      Khukie_Air > New folder
    <!-- 디렉토리 -->
    </v-card-title>
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
            <v-spacer />
            <!-- 버튼 구현-->
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
          </v-toolbar>
        </template>
        <!-- 표 내부의 수정부-->
        <template v-slot:item.actions="{ item }">
          <v-icon
            small
            class="mr-2"
            @click="HashItem(item)"
          >
            mdi-pound
          </v-icon>
          <v-icon
            small
            class="mr-2"
            @click="DownLoadItem(item)"
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
        </template>
        <!-- 파일이 없는 경우 표시 -->
        <template v-slot:no-data>
          <v-btn color="brown darken-4" @click="initialize">
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
</template>

<script>
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
      { text: 'Actions', value: 'actions', sortable: false }
    ],
    file: [],
    editedIndex: -1,
    editedItem: {
      name: '',
      size: 0
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
    }
  },
  created () {
    this.initialize()
  },
  methods: {
    initialize () {
      this.file = [
        {
          name: '기러기',
          size: 159
        },
        {
          name: '까치',
          size: 237
        },
        {
          name: '자기소개서.hwp',
          size: 262
        },
        {
          name: '기말보고서.doc',
          size: 305
        }
      ]
    },
    editItem (item) {
      this.editedIndex = this.file.indexOf(item)
      this.editedItem = Object.assign({}, item)
      this.dialog = true
    },
    deleteItem (item) {
      const index = this.file.indexOf(item)
      confirm('Are you sure you want to delete this item?') && this.file.splice(index, 1)
    },
    close () {
      this.dialog = false
      this.$nextTick(() => {
        this.editedItem = Object.assign({}, this.defaultItem)
        this.editedIndex = -1
      })
    },
    save () {
      if (this.editedIndex > -1) {
        Object.assign(this.file[this.editedIndex], this.editedItem)
      } else {
        this.file.push(this.editedItem)
      }
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
