import { createRouter, createWebHistory } from 'vue-router'
import LoginView from '@/views/LoginView.vue'
import SignUpView from '@/views/SignUpView.vue'
import HomeView from '@/views/HomeView.vue'
import AuthorProfileView from '@/views/AuthorProfileView.vue'
import StreamView from '@/views/StreamView.vue'
import FriendsView from '@/views/FriendsView.vue'
import ExploreView from '@/views/ExploreView.vue'
import NotificationsView from '@/views/NotificationsView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: LoginView
    },
    {
      path: '/signup',
      name: 'signup',
      component: SignUpView
    },
    
    {
      path: '/login',
      name: 'login',
      component: LoginView
    },
    {
      path: '/stream',
      name: 'stream',
      component: StreamView
    },  
    {
      path: '/author/:displayName',
      name: 'author-profile',
      component: AuthorProfileView,
      props: true
    },
    {
      path: '/friends',
      name: 'friends',
      component: FriendsView,
    },
    {
      path: '/explore',
      name: 'explore',
      component: ExploreView,
    },
    {
      path: '/notifications',
      name: 'notifications',
      component: NotificationsView,
    },
    {
      path: '/authors/:id',
      name: 'profile',
      component: () => import('../views/ProfileView.vue'),
      props: true,
    },
    {
      path: '/authors/:authorUid/posts/:postUid',
      name: 'postDetail',
      component: () => import('../views/PostDetailView.vue'),
      props: true,
    },
    // Add other routes as needed
  ]
})

export default router
