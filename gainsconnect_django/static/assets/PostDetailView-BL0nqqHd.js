import{r as c,u as i,o as p,a as u,c as o,f as l,_,k as d,h as e}from"./index-C-M45ECf.js";const h={class:"px-8 py-6 bg-gray-900 text-white min-h-screen"},m={key:0},f={key:1},k={__name:"PostDetailView",setup(y){const s=c(null),a=d();return i(),p(async()=>{try{const t=a.params.authorUid,r=a.params.postUid,n=await u.get(`api/authors/${t}/posts/${r}/`);s.value=n.data}catch(t){console.error("Error fetching post",t)}}),(t,r)=>(e(),o("main",h,[s.value===null?(e(),o("div",m," loading post... ")):(e(),o("div",f,[l(_,{post:s.value},null,8,["post"])]))]))}};export{k as default};