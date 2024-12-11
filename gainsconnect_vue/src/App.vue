<script setup>
import { RouterView } from 'vue-router';
import { onMounted } from 'vue';
import { useAuthorStore } from '../stores/user';
import { setAxiosAuthToken } from './functions';
import Sidebar from '@/components/Sidebar.vue';

const authorStore = useAuthorStore();

//function to set the token in Axios default headers
//onMounted: this is the Vue Composition API equivalent of mounted. 
            //it ensures that the setAxiosAuthToken() function runs after the component is mounted.
//set the token in Axios headers when the app loads
onMounted(() => {
  setAxiosAuthToken();
  console.log("starting", authorStore);
  //authorStore.testMethod();
});
</script>

<template>
  <div class="flex min-h-screen bg-gray-800 text-white">
    <div v-if="authorStore.isAuthenticated" class="h-dvh bg-blue-300">
      <Sidebar />
    </div>
    <div class="h-dvh px-4 py-3 bg-gray-800 flex-grow overflow-y-auto min-h-screen">
      <RouterView />
    </div>
  </div>  
</template>
