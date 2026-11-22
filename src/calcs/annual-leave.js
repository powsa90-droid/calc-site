// 근로기준법 제60조: 1년 미만 1개월 개근 시 1일(최대 11일), 1년 80% 이상 출근 시 15일, 3년 이상 2년마다 1일 가산(최대 25일)
function p(v){const[y,m,d]=v.split('-').map(Number);return{y,m,d}}
function today(){const n=new Date();return`${n.getFullYear()}-${String(n.getMonth()+1).padStart(2,'0')}-${String(n.getDate()).padStart(2,'0')}`}
function monthsBetween(a,b){let m=(b.y-a.y)*12+(b.m-a.m);if(b.d<a.d)m--;return m}
const leaveFor=n=>Math.min(25,15+Math.floor((n-1)/2)); // n년 근속(만) 시 발생
C.onCalc(()=>{
  const sv=C.$('#start').value;if(!sv){C.show('res','<p class="msg">입사일을 입력해 주세요.</p>');return}
  const s=p(sv),b=p(C.$('#base').value||today());
  const months=monthsBetween(s,b);
  if(months<0){C.show('res','<p class="msg">기준일이 입사일보다 뒤여야 합니다.</p>');return}
  const yrs=Math.floor(months/12);
  let now,desc;
  if(yrs<1){now=Math.min(11,months);desc=`입사 1년 미만: 개근한 달마다 1일씩 생겨 지금까지 최대 ${now}일`}
  else{now=leaveFor(yrs);desc=`근속 ${yrs}년차 연차: ${now}일`}
  const total=Math.min(11,months)+Array.from({length:yrs},(_,i)=>leaveFor(i+1)).reduce((a,x)=>a+x,0);
  const daily=C.num('wage')*(C.num('hrs')||8);
  const unused=C.num('unused');
  const rows=[];for(let n=0;n<=Math.max(yrs+2,5)&&n<=25;n++)rows.push(n===0?['입사 첫해 (1년 미만)','최대 11일']:[`만 ${n}년 근속 시`,`${leaveFor(n)}일`]);
  C.show('res',`<div class="big">현재 연차<b>${now}일</b></div>
  <p class="how">${desc}. 입사 후 지금까지 생긴 연차는 모두 약 ${total}일입니다 (해마다 출근율 80% 이상, 매월 개근 가정).</p>
  ${C.rows([
    ['1일 통상임금',C.won(daily)],
    ['못 쓴 연차',`${unused}일`],
    ['미사용 연차수당',C.won(daily*unused),'sum']])}
  <div class="sched"><table><thead><tr><th style="text-align:left">근속</th><th>발생 연차</th></tr></thead><tbody>${rows.map(r=>`<tr><td style="text-align:left">${r[0]}</td><td>${r[1]}</td></tr>`).join('')}</tbody></table></div>`);
});
