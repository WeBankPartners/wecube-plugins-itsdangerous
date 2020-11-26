<template>
  <div class=" ">
    <DangerousPageTable :pageConfig="pageConfig"></DangerousPageTable>
    <ModalComponent :modelConfig="modelConfig">
      <div slot="rule">
        <div class="marginbottom params-each">
          <label class="col-md-2 label-name">{{ $t('hr_level') }}:</label>
          <Select v-model="modelConfig.addRow.level" style="width: 338px">
            <Option v-for="item in modelConfig.v_select_configs.levelOptions" :value="item.value" :key="item.value">
              {{ item.label }}
            </Option>
          </Select>
        </div>
        <div class="marginbottom params-each">
          <label class="col-md-2 label-name">{{ $t('effect_on') }}:</label>
          <Select v-model="modelConfig.addRow.effect_on" style="width: 338px" @on-change="changeEffectOn">
            <Option v-for="item in modelConfig.v_select_configs.effectOptions" :value="item.value" :key="item.value">
              {{ item.label }}
            </Option>
          </Select>
        </div>
        <div class="marginbottom params-each">
          <label class="col-md-2 label-name">{{ $t('match_type') }}:</label>
          <Select v-model="modelConfig.addRow.match_type" style="width: 338px">
            <Option v-for="item in matchOptions" :value="item.value" :key="item.value">
              {{ item.label }}
            </Option>
          </Select>
        </div>
        <div class="marginbottom params-each">
          <label class="col-md-2 label-name">{{ $t('match_param_id') }}:</label>
          <Select
            v-model="modelConfig.addRow.match_param_id"
            :disabled="modelConfig.addRow.match_type === 'filter'"
            style="width: 338px"
            clearable
          >
            <Option v-for="item in modelConfig.v_select_configs.matchParamOption" :value="item.value" :key="item.value">
              {{ item.label }}
            </Option>
          </Select>
        </div>
      </div>
    </ModalComponent>
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
    display: true,
    render: item => {
      return item.enabled ? 'Yes' : 'No'
    }
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
    value: 'match_param.name', // 调用参数
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
          {
            label: 'match_value',
            value: 'match_value',
            v_validate: 'required:true',
            placeholder: '',
            disabled: false,
            type: 'text'
          },
          { label: 'hr_enabled', value: 'enabled', placeholder: '', disabled: false, type: 'checkbox' },
          { name: 'rule', type: 'slot' }
        ],
        addRow: {
          // [通用]-保存用户新增、编辑时数据
          name: null,
          description: null,
          enabled: true,
          level: 'high',
          effect_on: 'script',
          match_type: 'cli',
          match_value: '',
          match_param_id: null
        },
        v_select_configs: {
          levelOptions: [
            { label: 'critical', value: 'critical' },
            { label: 'high', value: 'high' },
            { label: 'medium', value: 'medium' },
            { label: 'low', value: 'low' }
          ],
          effectOptions: [
            { label: 'param', value: 'param' },
            { label: 'script', value: 'script' }
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
  watch: {
    matchOptions: function (val) {
      this.modelConfig.addRow.match_type = val.length > 1 ? this.modelConfig.addRow.match_type || 'cli' : 'filter'
    },
    'modelConfig.addRow.match_type': function (val) {
      if (val !== 'filter' && val) {
        this.getConfigData(val)
      }
    }
  },
  computed: {
    matchOptions: function () {
      let res = []
      if (this.modelConfig.addRow.effect_on === 'script') {
        res = [
          { label: 'cli', value: 'cli' },
          { label: 'sql', value: 'sql' },
          { label: 'text', value: 'text' },
          { label: 'fulltext', value: 'fulltext' }
        ]
      } else {
        res = [{ label: 'filter', value: 'filter' }]
      }
      return res
    }
  },
  mounted () {
    this.initTableData()
    this.getConfigData()
  },
  methods: {
    changeEffectOn () {
      this.modelConfig.addRow.match_type = ''
    },
    async initTableData () {
      const params = this.$itsCommonUtil.managementUrl(this)
      const { status, data } = await getTableData(params)
      if (status === 'OK') {
        this.pageConfig.table.tableData = data.data
        this.pageConfig.pagination.total = data.count
      }
    },
    async getConfigData () {
      // eslint-disable-next-line no-unused-vars
      let params = ''
      if (this.modelConfig.addRow.match_type === 'cli') {
        params = 'matchparams?type=cli'
      }
      if (['sql', 'text', 'fulltext'].includes(this.modelConfig.addRow.match_type)) {
        params = 'matchparams?type=regex'
      }
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
      this.modelConfig.addRow.enabled = true
      this.modelConfig.addRow.level = 'high'
      this.modelConfig.addRow.effect_on = 'script'
      this.modelConfig.addRow.match_type = 'cli'
      this.modelConfig.isAdd = true
      this.$root.JQ('#add_edit_Modal').modal('show')
    },
    async addPost () {
      this.modelConfig.addRow.enabled = Number(this.modelConfig.addRow.enabled)
      const { status, message } = await addTableRow(this.pageConfig.CRUD, [this.modelConfig.addRow])
      if (status === 'OK') {
        this.initTableData()
        this.$Message.success(message)
        this.$root.JQ('#add_edit_Modal').modal('hide')
      }
    },
    async editF (rowData) {
      this.id = rowData.id
      this.modelConfig.isAdd = false
      this.modelTip.value = rowData[this.modelTip.key]
      this.modelConfig.addRow = this.$itsCommonUtil.manageEditParams(this.modelConfig.addRow, rowData)
      this.$root.JQ('#add_edit_Modal').modal('show')
    },
    async editPost () {
      this.modelConfig.addRow.enabled = Number(this.modelConfig.addRow.enabled)
      const { status, message } = await editTableRow(this.pageConfig.CRUD, this.id, this.modelConfig.addRow)
      if (status === 'OK') {
        this.initTableData()
        this.$Message.success(message)
        this.$root.JQ('#add_edit_Modal').modal('hide')
      }
    },
    deleteConfirmModal (rowData) {
      this.$Modal.confirm({
        title: rowData.name,
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
