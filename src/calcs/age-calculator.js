// 민법 제158조 (2023.6.28 시행): 나이는 출생일을 산입해 만 나이로 계산
const ZOD=['원숭이','닭','개','돼지','쥐','소','호랑이','토끼','용','뱀','말','양'];
function p(v){const[y,m,d]=v.split('-').map(Number);return{y,m,d,t:Date.UTC(y,m-1,d)}}
function today(){const n=new Date();return`${n.getFullYear()}-${String(n.getMonth()+1).padStart(2,'0')}-${String(n.getDate()).padStart(2,'0')}`}
C.onCalc(()=>{
  const bv=C.$('#birth').value;if(!bv){C.show('res','<p class="msg">생년월일을 입력해 주세요.</p>');return}
  const b=p(bv),t=p(C.$('#base').value||today());
  if(t.t<b.t){C.show('res','<p class="msg">기준일이 생년월일보다 뒤여야 합니다.</p>');return}
  let age=t.y-b.y;if(t.m<b.m||(t.m===b.m&&t.d<b.d))age--;
  const yearAge=t.y-b.y,korAge=yearAge+1;
  let ny=t.y;let next=Date.UTC(ny,b.m-1,b.d);if(next<t.t){ny++;next=Date.UTC(ny,b.m-1,b.d)}
  const dday=Math.round((next-t.t)/864e5);
  const lived=Math.round((t.t-b.t)/864e5)+1;
  C.show('res',`<div class="big">만 나이<b>${age}세</b></div>
  ${C.rows([
    ['연 나이 (기준연도 − 출생연도)',`${yearAge}세`],
    ['세는 나이 (예전 한국식)',`${korAge}세`],
    ['띠',`${ZOD[b.y%12]}띠`],
    ['다음 생일까지',dday===0?'오늘이 생일입니다':`${dday}일`],
    ['태어난 날부터',`${C.fmt(lived)}일째`]])}`);
});
