import { defineStore } from "pinia";
import { jwt_decode } from "jwt-decode";

export const useAuthorStore = defineStore('author', {
    state: () => ({
        isAuthenticated: false,
        id: null,
        uid: null,
        displayName: null,
        profileImage: null,
        biography: null,
        email: null,
        githubUser: null,
        accessToken: null,
        refreshToken: null,
    }),
    actions: {
        logout() {
            this.isAuthenticated = false;
            this.id = null;
            this.displayName = null;
            this.profileImage = null;
            this.biography = null;
            this.email = null;
            this.githubUser = null;
            this.accessToken = null;
            this.refreshToken = null;

            localStorage.removeItem('accessToken');
            localStorage.removeItem('refreshToken');
        },
        setInfo(data) {
            this.isAuthenticated = true;
            this.id = data['id'];
            this.uid = data['id'].split('/').pop();
            this.displayName = data['displayName'];
            this.profileImage = data['profileImage'];
            this.biography = data['biography'];
            this.email = data['email'];
            this.githubUser = data['github'];
            this.accessToken = data['access'];
            this.refreshToken = data['refresh'];
        },
        changeInfo(data) {
            this.displayName = data['displayName'];
            this.profileImage = data['profileImage'];
            this.biography = data['biography'];
            this.email = data['email'];
            this.githubUser = data['github'];
        },
        loadTokens() {
            const accessToken = localStorage.getItem('accessToken');
            const refreshToken = localStorage.getItem('refreshToken');

            if (accessToken && refreshToken) {
                this.isAuthenticated = true;
                this.accessToken = accessToken;
                this.refreshToken = refreshToken;

                const decoded = jwt_decode(accessToken);
                console.log("deocded:", decoded);
            }
        },
        testMethod() {
            console.log("Test method works");
        }
    },
});
