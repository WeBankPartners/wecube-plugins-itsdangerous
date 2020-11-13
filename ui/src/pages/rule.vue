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
    title: 'hr_name',
    value: 'name',
    display: true
  },
  {
    title: 'hr_description', // 不必
    value: 'description',
    display: true
  },
  {
    title: 'hr_enabled',
    value: 'enabled',
    display: true
  },
  {
    title: 'hr_level',
    value: 'level', // 优先级
    display: true
  },
  {
    title: 'effect_on',
    value: 'effect_on', // 作用域
    display: true
  },
  {
    title: 'match_type',
    value: 'match_type', // 匹配方式
    display: true
  },
  {
    title: 'match_value',
    value: 'match_value', // 匹配表达式
    display: true
  },
  {
    title: 'match_param_id', // 不必
    value: 'match_param_id', // 调用参数
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
        CRUD: 'rules',
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
        modalTitle: 'hr_rule',
        isAdd: true,
        config: [
          {
            label: 'hr_name',
            value: 'name',
            placeholder: 'tips.inputRequired',
            v_validate: 'required:true|min:2|max:60',
            disabled: false,
            type: 'text'
          },
          { label: 'hr_description', value: 'description', placeholder: '', disabled: false, type: 'text' },
          { label: 'hr_level', value: 'level', max: 10, min: 0, placeholder: '', disabled: false, type: 'inputNumber' },
          // {
          //   label: 'effect_on',
          //   value: 'effect_on',
          //   option: 'effectOptions',
          //   v_validate: 'required:true',
          //   placeholder: '',
          //   disabled: false,
          //   type: 'select'
          // },
          // {
          //   label: 'match_type',
          //   value: 'match_type',
          //   option: 'matchOptions',
          //   v_validate: 'required:true',
          //   placeholder: '',
          //   disabled: false,
          //   type: 'select'
          // },
          // {
          //   label: 'match_value',
          //   value: 'match_value',
          //   v_validate: 'required:true',
          //   placeholder: '',
          //   disabled: false,
          //   type: 'text'
          // },
          // {
          //   label: 'match_param_id',
          //   value: 'match_param_id',
          //   option: 'matchParamOption',
          //   placeholder: '',
          //   disabled: false,
          //   type: 'select'
          // },
          { label: 'hr_enabled', value: 'enabled', placeholder: '', disabled: false, type: 'checkbox' }
        ],
        addRow: {
          // [通用]-保存用户新增、编辑时数据
          name: null,
          description: null,
          enabled: true,
          level: 0,
          effect_on: 'param',
          match_type: 'filter',
          match_value: '',
          match_param_id: []
        },
        v_select_configs: {
          effectOptions: [
            { label: 'param', value: 'param' },
            { label: 'script', value: 'script' }
          ],
          matchOptions: [
            { label: 'filter', value: 'filter' },
            { label: 'cli', value: 'cli' },
            { label: 'sql', value: 'sql' },
            { label: 'text', value: 'text' },
            { label: 'fulltext', value: 'fulltext' }
          ],
          matchParamOption: []
        }
      },
      modelTip: {
        key: 'name',
        value: null
      },
      id: ''
    }
  },
  mounted () {
    this.initData()
  },
  methods: {
    async initData () {
      const params = this.$commonUtil.managementUrl(this)
      const { status, data } = await getTableData(params)
      if (status === 'OK') {
        this.pageConfig.table.tableData = data.data
        this.pageConfig.pagination.total = data.count
      }
    },
    async getConfigData () {
      const params = 'matchparams'
      const { status, data } = await getTableData(params)
      if (status === 'OK') {
        this.modelConfig.v_select_configs.matchParamOption = data.data.map(item => {
          return {
            label: item.name,
            value: item.id
          }
        })
      }
    },
    async add () {
      await this.getConfigData()
      this.modelConfig.addRow.effect_on = 'param'
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
    async editF (rowData) {
      this.id = rowData.id
      this.modelConfig.isAdd = false
      this.modelTip.value = rowData[this.modelTip.key]
      this.modelConfig.addRow = this.$commonUtil.manageEditParams(this.modelConfig.addRow, rowData)
      await this.getConfigData()
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
        title: 123,
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
