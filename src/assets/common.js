// 공통 도우미: 숫자 입력 콤마, 포맷, 결과 표시
(function(){
  const $=s=>document.querySelector(s);
  const fmt=n=>(Math.round(n)||0).toLocaleString('ko-KR');
  const won=n=>fmt(n)+'원';
  const num=id=>{const el=document.getElementById(id);if(!el)return 0;const v=String(el.value).replace(/[^0-9.\-]/g,'');return v===''?0:parseFloat(v)};
  const radio=name=>{const el=document.querySelector(`input[name="${name}"]:checked`);return el?el.value:''};
  const floor10=n=>Math.floor(n/10)*10;
  function bindMoney(){
    document.querySelectorAll('input[data-money]').forEach(el=>{
      const f=()=>{const p=el.selectionStart,len=el.value.length;const d=el.value.replace(/[^0-9]/g,'');el.value=d?Number(d).toLocaleString('ko-KR'):'';const np=p+(el.value.length-len);try{el.setSelectionRange(np,np)}catch(e){}};
      el.addEventListener('input',f);f();
    });
  }
  function rows(list){
    return '<table class="kv">'+list.map(r=>`<tr class="${r[2]||''}"><td>${r[0]}</td><td>${r[1]}</td></tr>`).join('')+'</table>';
  }
  function show(id,html){const el=document.getElementById(id);el.innerHTML=html;el.classList.add('show');if(window.innerWidth<700)el.scrollIntoView({behavior:'smooth',block:'start'})}
  function onCalc(fn){
    const form=document.getElementById('calcForm');
    form.addEventListener('submit',e=>{e.preventDefault();fn()});
    const r=form.querySelector('[data-reset]');
    if(r)r.addEventListener('click',()=>{setTimeout(()=>{bindMoney();document.querySelectorAll('.result').forEach(x=>x.classList.remove('show'))},0)});
  }
  window.C={$,fmt,won,num,radio,floor10,rows,show,onCalc,bindMoney};
  document.addEventListener('DOMContentLoaded',bindMoney);
})();
