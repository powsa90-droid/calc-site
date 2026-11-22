// 주택공급에 관한 규칙 별표1: 무주택기간 32점 + 부양가족 35점 + 청약통장 가입기간 17점 = 84점
function p(v){const[y,m,d]=v.split('-').map(Number);return{y,m,d}}
function today(){const n=new Date();return`${n.getFullYear()}-${String(n.getMonth()+1).padStart(2,'0')}-${String(n.getDate()).padStart(2,'0')}`}
function months(a,b){let m=(b.y-a.y)*12+(b.m-a.m);if(b.d<a.d)m--;return m}
const later=(a,b)=>(a.y*1e4+a.m*100+a.d)>(b.y*1e4+b.m*100+b.d)?a:b;
const earlier=(a,b)=>later(a,b)===a?b:a;
const ds=x=>`${x.y}.${String(x.m).padStart(2,'0')}.${String(x.d).padStart(2,'0')}`;
C.onCalc(()=>{
  const t=p(today());
  const bv=C.$('#birth').value,av=C.$('#acc').value;
  if(!bv||!av){C.show('res','<p class="msg">생년월일과 청약통장 가입일을 입력해 주세요.</p>');return}
  const b=p(bv),own=C.radio('own')==='1';
  let s1=0,from=null,nm=0;
  if(!own){
    const at30={y:b.y+30,m:b.m,d:b.d};
    from=at30;
    if(C.$('#marry').value)from=earlier(at30,p(C.$('#marry').value));
    if(C.$('#lost').value)from=later(from,p(C.$('#lost').value));
    nm=months(from,t);
    s1=nm<0?0:Math.min(32,2*(Math.floor(nm/12)+1));
  }
  const fam=Math.max(0,Math.round(C.num('fam')));
  const s2=Math.min(35,5+5*fam);
  const am=months(p(av),t);
  const s3=am<0?0:am<6?1:am<12?2:Math.min(17,2+Math.floor(am/12));
  const tot=s1+s2+s3;
  const y=m=>`${Math.floor(m/12)}년 ${m%12}개월`;
  C.show('res',`<div class="big">청약 가점 합계 (84점 만점)<b>${tot}점</b></div>
  ${C.rows([
    [own?'무주택기간 (주택 소유 중)':nm<0?`무주택기간 (기산일 ${ds(from)} 이전)`:`무주택기간 ${y(nm)} (기산일 ${ds(from)})`,`${s1} / 32점`],
    [`부양가족 ${fam}명`,`${s2} / 35점`],
    [`청약통장 가입 ${am<0?'0개월':y(am)}`,`${s3} / 17점`],
    ['합계',`${tot} / 84점`,'sum']])}
  <p class="how">무주택기간은 만 30세가 된 날과 혼인신고일 중 빠른 날부터 셉니다. 그 뒤에 집을 처분했다면 처분일부터 다시 셉니다. 최종 점수는 청약홈의 자격 확인 결과를 기준으로 하세요.</p>`);
});
