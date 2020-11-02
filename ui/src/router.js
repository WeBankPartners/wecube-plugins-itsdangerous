import Vue from 'vue'
import Router from 'vue-router'

Vue.use(Router)
export default new Router({
  routes: [
    {
      path: '/',
      name: 'IndexPage',
      redirect: '/homepage/policy',
      component: () => import('@/pages/index'),
      children: [
        {
          path: '/homepage',
          name: 'homepage',
          component: () => import('@/pages/home-page'),
          params: {},
          props: true,
          children: [
            {
              path: 'policy',
              name: 'policy',
              title: '对象管理',
              meta: {},
              component: () => import('@/pages/policy')
            },
            {
              path: 'rule',
              name: 'rule',
              title: '组管理',
              meta: {},
              component: () => import('@/pages/rule')
            },
            {
              path: 'subjects',
              name: 'subjects',
              title: '阈值配置',
              meta: {},
              component: () => import('@/pages/subjects')
            },
            {
              path: 'targets',
              name: 'targets',
              title: '关键字配置',
              meta: {},
              component: () => import('@/pages/targets')
            },
            {
              path: 'match-params',
              name: 'match-params',
              title: '资源层级',
              meta: {},
              component: () => import('@/pages/match-params')
            },
            {
              path: 'boxes',
              name: 'boxes',
              title: '资源层级',
              meta: {},
              component: () => import('@/pages/boxes')
            }
          ]
        }
      ]
    }
  ]
})
