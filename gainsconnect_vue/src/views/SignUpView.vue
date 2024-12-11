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
            Already have an account?
            <RouterLink to="/login" class="underline text-purple-400 hover:text-purple-300">Click here</RouterLink> 
            to login!
        </p>
            <!--Form for signing up-->
            <form class="space-y-3" @submit.prevent="signup">
                <!--Display Name field-->
                <div>
                    <label class="block text-gray-400">Display Name</label>
                    <input v-model="displayName" type="text" placeholder="Enter display name" 
                        class="w-full mt-2 py-4 px-6 bg-gray-700 text-white border border-gray-600 
                        rounded-lg focus:border-purple-500 focus:outline-none"/>
                </div>
                <!--Username field-->
                <div>
                    <label class="block text-gray-400">Username</label>
                    <input v-model="username" type="text" placeholder="Enter username" 
                        class="w-full mt-2 py-4 px-6 bg-gray-700 text-white border border-gray-600 
                        rounded-lg focus:border-purple-500 focus:outline-none"/>
                </div>
                <!--Email field-->
                <div>
                    <label class="block text-gray-400">Email</label>
                    <input v-model="email" type="email" placeholder="Enter email" 
                        class="w-full mt-2 py-4 px-6 bg-gray-700 text-white border border-gray-600 
                        rounded-lg focus:border-purple-500 focus:outline-none"/>
                </div>
                <!--Password field-->
                <div>
                    <label class="block text-gray-400">Password</label>
                    <input v-model="password" type="password" placeholder="Your password" 
                    class="w-full mt-2 py-4 px-6 bg-gray-700 text-white border border-gray-600 
                    rounded-lg focus:border-purple-500 focus:outline-none" />
                </div>
                <!--Confirm password field-->
                <div>
                    <label class="block text-gray-400">Confirm Password</label>
                    <input v-model="confirmPassword" type="password" placeholder="Confirm password" 
                    class="w-full mt-2 py-4 px-6 bg-gray-700 text-white border border-gray-600 
                    rounded-lg focus:border-purple-500 focus:outline-none" />
                </div>

                <!-- GitHub Username field -->
                <div>
                    <label class="block text-gray-400">GitHub Username (optional)</label>
                    <input v-model="github" type="text" placeholder="Enter GitHub username" 
                        class="w-full mt-2 py-4 px-6 bg-gray-700 text-white border border-gray-600 
                        rounded-lg focus:border-purple-500 focus:outline-none"/>
                </div>

                <!--Submit button-->
                <div>
                    <button class="mt-4 w-full py-4 px-6 bg-purple-600 text-white rounded-lg hover:bg-purple-500 transition-colors" 
                    type="submit">Sign Up</button>
                </div>
            </form>
        </div>
        </div>
  </div>

  <!-- Sign up success message -->
  <div v-if="showSuccess" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
    <div class="bg-gray-800 p-6 rounded-lg shadow-xl max-w-md">
      <div class="text-center">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-12 w-12 text-green-500 mx-auto mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
        <h3 class="text-xl font-bold mb-4">Signup Successful!</h3>
        <p class="mb-6">Your account has been created. Please log in to continue.</p>
        <button 
          @click="goToLogin"
          class="px-6 py-2 bg-purple-600 rounded hover:bg-purple-500 transition-colors"
        >
          Go to Login
        </button>
      </div>
    </div>
  </div>
</template>
    
<script>
    import axios from 'axios';
    import api from '@/services/api'; // Adjust the path based on your project structure

    export default {
    data() {
        return {
        biceps: import.meta.env.PROD ? '/static/images/biceps.png' : '/images/biceps.png',
        username: '',
        email: '',
        displayName: '',
        password: '',
        confirmPassword: '',
        github: '',
        showSuccess: false,
        };
    },
    methods: {        
        signup() {
        if (this.password !== this.confirmPassword) {
            alert('Passwords do not match!');
            return;
        }

        api.post('/authors/signup/', {
            username: this.username,
            email: this.email,
            password: this.password,
            displayName: this.displayName,
            github: this.github
        })
        .then(response => {
            this.showSuccess = true;
        })
        .catch(error => {
            alert('Signup Failed: ' + error.response.data);
            console.error('Signup Failed:', error);
        });
        },

        goToLogin() {
            this.showSuccess = false;
            this.$router.push('/login');
        }
    }
    }
</script>