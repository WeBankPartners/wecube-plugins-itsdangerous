<template>
  <div class=" ">
    <DangerousPageTable :pageConfig="pageConfig"></DangerousPageTable>
    <ModalComponent :modelConfig="modelConfig">
      <template #plugin-params>
        <div class="marginbottom params-each">
          <label class="col-md-2 label-name">{{ $t('content_type') }}:</label>
          <Select v-model="modelConfig.addRow.content_type" style="width: 338px">
            <Option
              v-for="item in modelConfig.v_select_configs.contentTypeOptions"
              :value="item.value"
              :key="item.value"
            >
              {{ item.label }}
            </Option>
          </Select>
        </div>
      </template>
    </ModalComponent>
  </div>
</template>

<script>
import { getTableData, addTableRow, editTableRow, deleteTableRow } from '@/api/server'
let tableEle = [
  {
    title: 'service',
    value: 'service', // 插件
    display: true
  },
  {
    title: 'content_type', // 不必
    value: 'content_type', // 脚本类型
    display: true
  },
  {
    title: 'content_field',
    value: 'content_field', // 脚本字段
    display: true
  },
  {
    title: 'endpoint_field', // 脚本地址
    value: 'endpoint_field',
    display: true
  },
  {
    title: 'hr_created_by',
    value: 'created_by', //
    display: true
  },
  {
    title: 'hr_created_time',
    value: 'created_time', //
    display: true
  },
  {
    title: 'hr_updated_by',
    value: 'updated_by', //
    display: true
  },
  {
    title: 'hr_updated_time',
    value: 'updated_time', //
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
        CRUD: 'service-scripts',
        researchConfig: {
          input_conditions: [
            {
              value: 'service__icontains',
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
        modalTitle: 'hr_plugin_params',
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
          { name: 'plugin-params', type: 'slot' },
          {
            label: 'content_field',
            value: 'content_field',
            v_validate: '',
            placeholder: '',
            disabled: false,
            type: 'text'
          },
          {
            label: 'endpoint_field',
            value: 'endpoint_field',
            v_validate: '',
            placeholder: '',
            disabled: false,
            type: 'text'
          }
        ],
        addRow: {
          // [通用]-保存用户新增、编辑时数据
          service: null,
          content_type: null,
          content_field: null,
          endpoint_field: ''
        },
        v_select_configs: {
          contentTypeOptions: [
            { label: 'shell', value: 'shell' },
            { label: 'sql', value: 'sql' }
          ]
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
    this.initTableData()
  },
  methods: {
    async initTableData () {
      const params = this.$itsCommonUtil.managementUrl(this)
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
      const { status, message } = await addTableRow(this.pageConfig.CRUD, [this.modelConfig.addRow])
      if (status === 'OK') {
        this.initTableData()
        this.$Message.success(message)
        this.$root.JQ('#add_edit_Modal').modal('hide')
      }
    },
    editF (rowData) {
      this.id = rowData.id
      this.modelConfig.isAdd = false
      this.modelTip.value = rowData[this.modelTip.key]
      this.modelConfig.addRow = this.$itsCommonUtil.manageEditParams(this.modelConfig.addRow, rowData)
      this.$root.JQ('#add_edit_Modal').modal('show')
    },
    async editPost () {
      const { status, message } = await editTableRow(this.pageConfig.CRUD, this.id, this.modelConfig.addRow)
      if (status === 'OK') {
        this.initTableData()
        this.$Message.success(message)
        this.$root.JQ('#add_edit_Modal').modal('hide')
      }
    },
    deleteConfirmModal (rowData) {
      this.$Modal.confirm({
        title: this.$t('delete_confirm') + rowData.service,
        'z-index': 1000000,
        onOk: async () => {
          const { status, message } = await deleteTableRow(this.pageConfig.CRUD, rowData.id)
          if (status === 'OK') {
            this.initTableData()
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
