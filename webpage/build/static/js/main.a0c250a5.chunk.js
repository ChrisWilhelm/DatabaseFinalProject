(this.webpackJsonpwebpage=this.webpackJsonpwebpage||[]).push([[0],{44:function(e,t,n){},45:function(e,t,n){},75:function(e,t,n){"use strict";n.r(t);var c=n(2),r=n.n(c),a=n(12),i=n.n(a),s=(n(44),n(11)),o=(n.p,n(45),n(3));var l=function(){var e=window;return{width:e.innerWidth,height:e.innerHeight}}(),u=l.width;l.height;var d=function(e){var t=e.query,n=e.setQuery,c=e.searchHook,r=e.onSubmit;return Object(o.jsxs)("form",{className:"search-bar",style:{display:"flex",height:75,width:.6*u,borderRadius:50,justifyContent:"center",alignItems:"center"},children:[Object(o.jsx)("label",{className:"search-bar-label",style:{marginLeft:50,marginRight:10},children:Object(o.jsx)("p",{children:"Search:"})}),Object(o.jsx)("input",{className:"search-input",type:"text",value:t,onChange:function(e){return n(e.target.value)},style:{border:0,padding:10,fontSize:25,flex:1}}),Object(o.jsx)("button",{className:"search-button",onClick:function(e){e.preventDefault(),c(),e.currentTarget.blur(),r()},style:{border:0,paddingLeft:35,paddingRight:50,borderBottomRightRadius:50,borderTopRightRadius:50,height:"100%",justifyContent:"center",alignItems:"center",display:"flex",backgroundColor:"#89cff0"},children:Object(o.jsx)("p",{style:{fontSize:24},children:"Submit"})})]})},h=n(21),b="http://44.202.10.14:8000",j=(n(52),n(80)),f=n(83),p=n(79),g=n(84),O=n(81),m=n(82),y=["January","February","March","April","May","June","July","August","September","October","November","December"];function x(e,t,n,c){t(!0),c(!1);var r=b+"/query?q="+e;console.log(r),fetch(r,{headers:{Accept:"*/*","Content-Type":"application/json"}}).then((function(e){if(t(!1),200===e.status)return e.json();c(!0)})).then((function(e){n(e.results)})).catch((function(e){return e}))}var N={LEFT:"#0275d8",LEAN_LEFT:"#89CFF0",CENTER:"#888888",LEAN_RIGHT:"#ffcccb",RIGHT:"#d9534f",MIXED:"#b19cd9"},v={LEFT:"LEFT",LEAN_LEFT:"LEFT LEANING",CENTER:"CENTER LEANING",LEAN_RIGHT:"RIGHT LEANING",RIGHT:"RIGHT",MIXED:"MIXED"};var T=function(e){var t=e.rating,n=e.index,r=Object(c.useState)(!1),a=Object(s.a)(r,2),i=a[0],l=a[1],u="Popover"+n.toString(),d=n%2===0?"right":"left";return Object(o.jsxs)(p.a,{id:u,className:"rating-button",onMouseEnter:function(){l(!0)},onMouseLeave:function(){l(!1)},style:{display:"flex",width:"100%",height:"100%",border:0,backgroundColor:"transparent"},children:[Object(o.jsx)(j.a,{color:"#fff"}),Object(o.jsx)(g.a,{target:u,placement:d,isOpen:i,fade:!0,children:Object(o.jsxs)("div",{style:{backgroundColor:"#fff",borderRadius:12,padding:5,paddingLeft:10,paddingRight:10,margin:25,display:"flex",justifyContent:"center",alignItems:"center",flexDirection:"column",maxWidth:250},children:[Object(o.jsx)(O.a,{children:"Political Bias"}),Object(o.jsxs)(m.a,{style:{marginLeft:20,marginRight:20,fontFamily:"Noto Sans SC"},children:["This site has a tendency to publish content rated as ",Object(o.jsx)("p",{style:{color:N[t],textAlign:"center"},children:v[t]})]})]})})]})},E=function(e){var t=e.article,n=e.index,c=e.query,r=t.date?new Date(t.date):null,a=r?y[r.getMonth()]+" "+r.getDate()+", "+r.getFullYear():"Date not available";return Object(o.jsxs)(h.VerticalTimelineElement,{className:"vertical-timeline-element--work",contentStyle:{background:"rgb(33, 150, 243)",color:"#fff"},contentArrowStyle:{borderRight:"7px solid  rgb(33, 150, 243)"},date:a,icon:Object(o.jsx)(T,{index:n,rating:t.rating}),iconStyle:{background:"rgb(33, 150, 243)",color:"#fff"},children:[Object(o.jsx)("h2",{style:{color:"#fff"},children:t.title}),Object(o.jsx)("h3",{style:{color:"#ccc"},children:t.publisher}),Object(o.jsx)("h4",{className:"article-summary",children:t.summary}),Object(o.jsxs)("div",{style:{display:"flex",flexDirection:"row",justifyContent:"space-between"},children:[Object(o.jsxs)("div",{children:[Object(o.jsx)("a",{className:"article-link",target:"blank",href:t.link,children:"Article"}),Object(o.jsx)("a",{className:"site-link",target:"blank",href:t.site,children:"Site Home Page"})]}),Object(o.jsx)(w,{query:c,doc_id:t.doc_id})]})]})},S="SET_RELEVANT",R="SET_IRRELEVANT",C="UNDO_RELEVANT",L="UNDO_IRRELEVANT",k=function(e,t,n){var c=[],r=[];n===S?c.push(e):n===R&&r.push(e);var a={q:t,undo:"False",relevant:c,irrelevant:r};fetch(b+"/query/update",{method:"POST",headers:{Accept:"*/*","Content-Type":"application/json"},body:JSON.stringify(a)}).then((function(e){return e})).catch((function(e){return e}))},A=function(e,t,n){var c=[],r=[];n===S?(c.push(e),c.push(e)):n===R&&(r.push(e),r.push(e));var a={q:t,undo:"False",relevant:c,irrelevant:r};fetch(b+"/query/update",{method:"POST",headers:{Accept:"*/*","Content-Type":"application/json"},body:JSON.stringify(a)}).then((function(e){return e})).catch((function(e){return e}))},I=function(e,t,n){var c=[],r=[];n===C?c.push(e):n===L&&r.push(e);var a={q:t,undo:"True",relevant:c,irrelevant:r};fetch(b+"/query/update",{method:"POST",headers:{Accept:"*/*","Content-Type":"application/json"},body:JSON.stringify(a)}).then((function(e){return console.log(e)})).catch((function(e){return e}))},w=function(e){var t=e.doc_id,n=e.query,r=Object(c.useState)(0),a=Object(s.a)(r,2),i=a[0],l=a[1];return Object(o.jsxs)("div",{children:[Object(o.jsx)("button",{style:{backgroundColor:1===i?"#90ee90":null},onClick:function(){l(1===i?0:1),function(e,t){t&&e&&(-1===i?A(t,e,S):0===i?k(t,e,S):I(t,e,C))}(n,t)},className:"thumb-button thumbs-up",children:Object(o.jsx)(f.b,{})}),Object(o.jsx)("button",{style:{backgroundColor:-1===i?"#ff6961":null},onClick:function(){l(-1===i?0:-1),function(e,t){t&&e&&(1===i?A(t,e,R):0===i?k(t,e,R):I(t,e,L))}(n,t)},className:"thumb-button thumbs-down",children:Object(o.jsx)(f.a,{})})]})},F=function(){var e=Object(c.useState)([]),t=Object(s.a)(e,2),n=t[0],r=t[1],a=Object(c.useState)(!1),i=Object(s.a)(a,2),l=i[0],u=i[1],b=Object(c.useState)(""),j=Object(s.a)(b,2),f=j[0],p=j[1],g=Object(c.useState)(!1),O=Object(s.a)(g,2),m=O[0],y=O[1],N=Object(c.useState)(!1),v=Object(s.a)(N,2),T=(v[0],v[1]),S=Object(c.useState)(""),R=Object(s.a)(S,2),C=R[0],L=R[1];return l?Object(o.jsxs)("div",{className:"app-container",children:[Object(o.jsx)("header",{className:"search-results-header",children:Object(o.jsx)(d,{searchHook:function(){u(!0),L(f)},setQuery:p,query:f,onSubmit:function(){x(f,y,r,T)}})}),m&&Object(o.jsx)("div",{className:"loader-container",children:Object(o.jsx)("div",{className:"loader"})}),!m&&Object(o.jsx)("div",{className:"timeline-container",children:Object(o.jsx)(h.VerticalTimeline,{children:n.map((function(e,t){return Object(o.jsx)(E,{article:e,index:t,query:C},t)}))})})]}):Object(o.jsx)("div",{className:"app-container",children:Object(o.jsxs)("header",{className:"App-header",children:[Object(o.jsx)("h1",{children:"NewsLine"}),Object(o.jsx)(d,{searchHook:function(){u(!0),L(f)},setQuery:p,query:f,onSubmit:function(){x(f,y,r,T)}})]})})},q=function(e){e&&e instanceof Function&&n.e(3).then(n.bind(null,85)).then((function(t){var n=t.getCLS,c=t.getFID,r=t.getFCP,a=t.getLCP,i=t.getTTFB;n(e),c(e),r(e),a(e),i(e)}))};i.a.render(Object(o.jsx)(r.a.StrictMode,{children:Object(o.jsx)(F,{})}),document.getElementById("root")),q()}},[[75,1,2]]]);
//# sourceMappingURL=main.a0c250a5.chunk.js.map