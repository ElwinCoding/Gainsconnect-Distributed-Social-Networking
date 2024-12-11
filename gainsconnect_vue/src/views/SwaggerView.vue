<template>
    <div>
      <h1>API Documentation</h1>
      <pre v-if="swaggerData">{{ swaggerData }}</pre>
      <p v-else>Loading...</p>
    </div>
  </template>
  
  <script>
  import { fetchSwaggerJSON } from '@/services/swaggerService';
  
  export default {
    data() {
      return {
        swaggerData: null
      };
    },
    async created() {
      try {
        this.swaggerData = await fetchSwaggerJSON();
      } catch (error) {
        console.error("Error loading Swagger data:", error);
      }
    }
  };
  </script>