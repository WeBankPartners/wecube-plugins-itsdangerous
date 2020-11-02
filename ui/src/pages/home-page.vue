<template>
  <div class="monitor-config-index">
    <Title :title="$t('menu.configuration')"></Title>
    <section>
      <Tabs :value="activeTab" @on-click="changeTab">
        <template v-for="(tabItem, tabIndex) in tabs">
          <TabPane :label="$t(tabItem.label)" :name="tabItem.path" :key="tabIndex"> </TabPane>
        </template>
      </Tabs>
      <router-view></router-view>
    </section>
  </div>
</template>

<script>
export default {
  name: '',
  data () {
    return {
      activeTab: '/homepage/policy',
      tabs: [
        { label: '策略', path: '/homepage/policy' },
        { label: '规则', path: '/homepage/rule' },
        { label: '角色', path: '/homepage/subjects' },
        { label: '目标对象', path: '/homepage/targets' },
        { label: '调用参数', path: '/homepage/match-params' },
        { label: '试盒', path: '/homepage/boxes' }
      ]
    }
  },
  mounted () {
    this.activeTab = this.$route.path
  },
  methods: {
    changeTab (path) {
      this.activeTab = path
      if (this.$route.path === path) return
      this.$router.push({ path: path })
    }
  },
  components: {}
}
</script>

<style lang="scss" scoped>
.home-page {
  align-items: center;
  background-color: #fff;
  display: flex;
  font-size: 75px;
  font-weight: 600;
  height: 100%;
  justify-content: center;
}
</style>
