const WD=['일','월','화','수','목','금','토'];
function p(v){const[y,m,d]=v.split('-').map(Number);return Date.UTC(y,m-1,d)}
function today(){const n=new Date();return Date.UTC(n.getFullYear(),n.getMonth(),n.getDate())}
const f=t=>{const x=new Date(t);return`${x.getUTCFullYear()}년 ${x.getUTCMonth()+1}월 ${x.getUTCDate()}일 (${WD[x.getUTCDay()]})`};
function sync(){const a=C.radio('mode')==='add';C.$('#b2').style.display=a?'none':'';C.$('#b3').style.display=a?'':'none'}
document.querySelectorAll('input[name="mode"]').forEach(el=>el.addEventListener('change',sync));
C.$('#calcForm').addEventListener('reset',()=>setTimeout(sync,0));
C.onCalc(()=>{
  const s=C.$('#d1').value?p(C.$('#d1').value):today();
  const inc=C.radio('inc')==='1'?1:0;
  if(C.radio('mode')==='add'){
    const n=Math.round(C.num('n'));
    const t=s+(n-inc)*864e5;
    C.show('res',`<div class="big">${n}일째 되는 날${inc?' (시작일 = 1일째)':' (시작일 다음 날 = 1일)'}<b>${f(t)}</b></div>
    ${C.rows([['시작일',f(s)],[`${n}일 후`,f(t),'sum']])}
    <div class="sched"><table><thead><tr><th style="text-align:left">기념일</th><th>날짜</th></tr></thead><tbody>${[100,200,300,365,500,1000].map(k=>`<tr><td style="text-align:left">${k}일</td><td>${f(s+(k-inc)*864e5)}</td></tr>`).join('')}</tbody></table></div>`);
    return;
  }
  const e=C.$('#d2').value?p(C.$('#d2').value):today();
  const diff=Math.round((e-s)/864e5);
  const days=diff+(diff>=0?inc:-inc);
  const label=diff>0?`D-${diff}`:diff<0?`D+${-diff}`:'D-day';
  C.show('res',`<div class="big">${f(s)} → ${f(e)}<b>${inc?`${Math.abs(days)}일째`:`${Math.abs(diff)}일 ${diff>=0?'남음':'지남'} (${label})`}</b></div>
  ${C.rows([['일수',`${C.fmt(Math.abs(days))}일`],['주 단위',`${Math.floor(Math.abs(days)/7)}주 ${Math.abs(days)%7}일`],['개월 환산 (30.44일)',`약 ${(Math.abs(days)/30.4375).toFixed(1)}개월`],['시간 환산',`${C.fmt(Math.abs(days)*24)}시간`]])}`);
});
sync();
