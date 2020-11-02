<template>
  <div class=" ">
    <PageTable :pageConfig="pageConfig"></PageTable>
    <ModalComponent :modelConfig="modelConfig"></ModalComponent>
  </div>
</template>

<script>
import { getTableData, addTableRow, editTableRow, deleteTableRow } from '@/api/server'
let tableEle = [
  {
    title: 'service',
    value: 'service',
    display: true
  },
  {
    title: 'content_type',
    value: 'content_type',
    display: true
  },
  {
    title: 'content_field',
    value: 'content_field',
    display: true
  },
  {
    title: 'endpoint_field',
    value: 'endpoint_field',
    display: true
  }
]
const btn = [
  { btn_name: 'button.edit', btn_func: 'editF' },
  { btn_name: 'button.remove', btn_func: 'deleteConfirmModal' }
]
export default {
  name: '',
  data () {
    return {
      pageConfig: {
        CRUD: 'boxes',
        researchConfig: {
          input_conditions: [
            {
              value: 'name__icontains',
              type: 'input',
              placeholder: 'placeholder.input',
              style: ''
            }
          ],
          btn_group: [
            {
              btn_name: 'button.search',
              btn_func: 'search',
              class: 'btn-confirm-f',
              btn_icon: 'fa fa-search'
            },
            {
              btn_name: 'button.add',
              btn_func: 'add',
              class: 'btn-cancel-f',
              btn_icon: 'fa fa-plus'
            }
          ],
          filters: {
            search: ''
          }
        },
        table: {
          tableData: [],
          tableEle: tableEle,
          // filterMoreBtn: 'filterMoreBtn',
          primaryKey: 'guid',
          btn: btn,
          pagination: this.pagination,
          handleFloat: true
        },
        pagination: {
          total: 0,
          page: 1,
          size: 10
        }
      },
      modelConfig: {
        modalId: 'add_edit_Modal',
        modalTitle: '试盒',
        isAdd: true,
        config: [
          {
            label: 'service',
            value: 'service',
            placeholder: 'tips.inputRequired',
            v_validate: 'required:true|min:2|max:60',
            disabled: false,
            type: 'text'
          },
          { label: 'content_type', value: 'content_type', placeholder: '', disabled: false, type: 'text' },
          { label: 'content_field', value: 'content_field', placeholder: '', disabled: false, type: 'text' },
          { label: 'endpoint_field', value: 'endpoint_field', placeholder: '', disabled: false, type: 'text' }
        ],
        addRow: {
          // [通用]-保存用户新增、编辑时数据
          service: null,
          content_type: null,
          content_field: null,
          endpoint_field: null
        }
      },
      modelTip: {
        key: 'service',
        value: null
      },
      id: ''
    }
  },
  mounted () {
    this.initData()
  },
  methods: {
    managementUrl () {
      let tableParams = this.pageConfig.CRUD
      const pp = {
        __offset: (this.pageConfig.pagination.page - 1) * this.pageConfig.pagination.size,
        __limit: this.pageConfig.pagination.size
      }
      const params = Object.assign({}, pp, this.pageConfig.researchConfig.filters)
      if (params) {
        let tmp = ''
        for (let key in params) {
          tmp = tmp + key + '=' + params[key] + '&'
        }
        tableParams = tableParams + '?' + tmp
      }
      return tableParams
    },
    async initData () {
      const params = this.managementUrl()
      const { status, data } = await getTableData(params)
      if (status === 'OK') {
        this.pageConfig.table.tableData = data.data
        this.pageConfig.pagination.total = data.count
      }
    },
    add () {
      this.modelConfig.isAdd = true
      this.$root.JQ('#add_edit_Modal').modal('show')
    },
    async addPost () {
      this.modelConfig.addRow.enabled = Number(this.modelConfig.addRow.enabled)
      const { status, message } = await addTableRow(this.pageConfig.CRUD, [this.modelConfig.addRow])
      if (status === 'OK') {
        this.initData()
        this.$Message.success(message)
        this.$root.JQ('#add_edit_Modal').modal('hide')
      }
    },
    editF (rowData) {
      this.id = rowData.id
      this.modelConfig.isAdd = false
      this.modelTip.value = rowData[this.modelTip.key]
      this.modelConfig.addRow.name = rowData.name
      this.modelConfig.addRow.description = rowData.description
      this.modelConfig.addRow.enabled = rowData.enabled
      this.$root.JQ('#add_edit_Modal').modal('show')
    },
    async editPost () {
      this.modelConfig.addRow.enabled = Number(this.modelConfig.addRow.enabled)
      const { status, message } = await editTableRow(this.pageConfig.CRUD, this.id, this.modelConfig.addRow)
      if (status === 'OK') {
        this.initData()
        this.$Message.success(message)
        this.$root.JQ('#add_edit_Modal').modal('hide')
      }
    },
    deleteConfirmModal (rowData) {
      this.$Modal.confirm({
        title: this.$t(this.modelConfig.modalTitle),
        'z-index': 1000000,
        onOk: async () => {
          const { status, message } = await deleteTableRow(this.pageConfig.CRUD, rowData.id)
          if (status === 'OK') {
            this.initData()
            this.$Message.success(message)
          }
        },
        onCancel: () => {}
      })
    }
  },
  components: {}
}
</script>

<style scoped lang="scss"></style>
