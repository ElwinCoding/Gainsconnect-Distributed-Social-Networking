<template>
  <div class="min-h-screen flex items-center justify-center">
    <div class="max-w-7x1 mx-auto grid grid-cols-2 items-center">
      <!--Left side, Logo-->
      <div>
        <div class="flex items-center space-x-4 pr-6">
        <img :src="biceps" alt="GainsConnect Logo" class="w-40 h-40"/>
        <div>
          <p class="font-extrabold text-7xl">GainsConnect</p>
        </div>
      </div>
      <p class="italic text-center text-2xl">
        Connect and Gain
      </p>
      </div>
      
      <!--Right side, login form-->
      <div class="pl-6 border-l border-s-gray-600 w-2/3">
        <p class="font-bold mb-5">
          Don't have an account?
          <RouterLink to="/signup" class="underline text-purple-400 hover:text-purple-300">Click here</RouterLink> 
          to sign up!
      </p>
        <!-- Form for logging in -->
        <form class="space-y-3 " @submit.prevent="login">
          <div>
            <label class="block text-gray-400">Username</label>
            <input v-model="username" type="text" placeholder="Your username" 
              class="w-full mt-2 py-4 px-6 bg-gray-700 text-white border border-gray-600 
              rounded-lg focus:border-purple-500 focus:outline-none"/>
          </div>
          <div>
            <label class="block text-gray-400">Password</label>
            <input v-model="password" type="password" placeholder="Your password" 
            class="w-full mt-2 py-4 px-6 bg-gray-700 text-white border border-gray-600 
              rounded-lg focus:border-purple-500 focus:outline-none" />
          </div>
          <!--Submit button-->
          <div>
            <button class="mt-4 w-full py-4 px-6 bg-purple-600 text-white rounded-lg hover:bg-purple-500 transition-colors" 
            type="submit">Login</button>
          </div>
        </form>
      </div>
    </div>

    <!-- Success message -->
    <div v-if="showSuccess" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div class="bg-gray-800 p-6 rounded-lg shadow-xl max-w-md">
        <div class="text-center">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-12 w-12 text-green-500 mx-auto mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <h3 class="text-xl font-bold mb-4">Welcome Back!</h3>
          <p class="mb-6">Login successful. Redirecting to your stream...</p>
          <Vue3Lottie
            :animationData="bicep"
            :height="100"
            :width="100"
            class="mx-auto mb-4"
          />
        </div>
      </div>
    </div>
  </div>
</template>
    
<script>
import { useAuthorStore } from '../../stores/user';
import { setAxiosAuthToken } from '@/functions';
import api from '@/services/api';
import { Vue3Lottie } from 'vue3-lottie';
import bicep from '@/assets/bicep.json';

export default {
  components: {
    Vue3Lottie
  },
  data() {
    return {
      biceps: import.meta.env.PROD ? '/static/images/biceps.png' : '/images/biceps.png',
      username: '',
      password: '',
      authorStore: useAuthorStore(),
      showSuccess: false,
      bicep: bicep,
    }
  },
  methods: {
    login() {

      //make a POST request to the login API endpoint with the entered credentials
      api.post('/authors/login/', {
        username: this.username,
        password: this.password,
      })
      .then(response => {

        // extract fields from the response
        const accessToken = response.data.access; 
        const refreshToken = response.data.refresh; 

        // Show success message and redirect after a delay
        this.showSuccess = true;
        setTimeout(() => {

          //on successful login, save the response in authorStore and tokens in localStorage
          this.authorStore.setInfo(response.data);
          localStorage.setItem('access_token', accessToken); 
          localStorage.setItem('refresh_token', refreshToken); 
          this.showSuccess = false;
          this.$router.push('/stream');
        }, 1500); // Redirect after timeout

        // set token for future requests
        setAxiosAuthToken();
      })
      .catch(error => {
        alert('Login failed: ' + error.response.data);
      });
    }
  }
};
</script>