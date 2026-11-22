// 근로자퇴직급여 보장법: 퇴직금 = 1일 평균임금 × 30일 × (재직일수/365)
// 퇴직소득세: 소득세법 제48조·제55조 (근속연수공제 → 환산급여 → 환산급여공제 → 기본세율 × 근속연수/12)
function d(v){const[y,m,dd]=v.split('-').map(Number);return new Date(Date.UTC(y,m-1,dd))}
const DAY=864e5;
function retireTax(pay,years){
  if(pay<=0)return{tax:0,local:0};
  const y=Math.max(1,years);
  let ded;
  if(y<=5)ded=1e6*y;else if(y<=10)ded=5e6+2e6*(y-5);else if(y<=20)ded=15e6+2.5e6*(y-10);else ded=40e6+3e6*(y-20);
  const conv=Math.max(0,pay-ded)*12/y;
  let cd;
  if(conv<=8e6)cd=conv;else if(conv<=7e7)cd=8e6+(conv-8e6)*0.6;else if(conv<=1e8)cd=45.2e6+(conv-7e7)*0.55;else if(conv<=3e8)cd=61.7e6+(conv-1e8)*0.45;else cd=151.7e6+(conv-3e8)*0.35;
  const base=Math.max(0,conv-cd);
  const b=[[14e6,.06,0],[5e7,.15,1.26e6],[8.8e7,.24,5.76e6],[1.5e8,.35,15.44e6],[3e8,.38,19.94e6],[5e8,.40,25.94e6],[1e9,.42,35.94e6],[Infinity,.45,65.94e6]];
  let t=0;for(const[l,r,k]of b)if(base<=l){t=base*r-k;break}
  const tax=Math.floor(Math.max(0,t)*y/12/10)*10;
  return{tax,local:Math.floor(tax*0.1/10)*10,ded,conv,cd,base};
}
function svcYears(sv,ev){ // 입사일~퇴직일(마지막 근무일 다음 날) 근속연수, 1년 미만 끝수는 1년
  const [a,b]=[sv,ev].map(v=>{const x=new Date(v);return{y:x.getUTCFullYear(),m:x.getUTCMonth(),d:x.getUTCDate()}});
  let mo=(b.y-a.y)*12+(b.m-a.m);let rem=b.d-a.d;if(rem<0){mo--;rem=1}
  return Math.max(1,Math.floor(mo/12)+((mo%12)||rem?1:0));
}
const fmtD=t=>{const x=new Date(t);return`${x.getUTCFullYear()}년 ${x.getUTCMonth()+1}월 ${x.getUTCDate()}일`};
C.onCalc(()=>{
  const s=C.$('#start').value,l=C.$('#last').value;
  if(!s||!l){C.show('res','<p class="msg">입사일과 마지막 근무일을 입력해 주세요.</p>');return}
  const S=d(s),E=new Date(d(l).getTime()+DAY);
  const days=Math.round((E-S)/DAY);
  if(days<=0){C.show('res','<p class="msg">마지막 근무일이 입사일보다 뒤여야 합니다.</p>');return}
  const B=new Date(E);B.setUTCMonth(B.getUTCMonth()-3);
  const d3=Math.round((E-B)/DAY);
  const wage3=C.num('wage3'),bonus=C.num('bonus'),leave=C.num('leave'),ord=C.num('ord');
  const total3=wage3+bonus*3/12+leave*3/12;
  let avg=total3/d3,used='평균임금';
  const ordDay=ord>0?ord/209*8:0;
  if(ordDay>avg){avg=ordDay;used='통상임금'}
  const pay=Math.floor(avg*30*days/365);
  const yrs=Math.floor(days/365),rem=days-yrs*365;
  const taxYears=svcYears(S.getTime(),E.getTime());
  const t=retireTax(pay,taxYears);
  const net=pay-t.tax-t.local;
  const due=E.getTime()+14*DAY;
  const warn=days<365?'<p class="msg">재직 기간이 1년 미만이면 법정 퇴직금 지급 대상이 아닙니다. 아래 금액은 참고용입니다.</p>':'';
  C.show('res',`<div class="big">예상 퇴직금 (세전)<b>${C.won(pay)}</b></div>
  <div class="big" style="margin-top:6px">세금을 뗀 예상 수령액 ${C.won(net)}</div>${warn}
  ${C.rows([
    ['재직일수',`${C.fmt(days)}일 (약 ${yrs}년 ${rem}일)`],
    ['퇴직일',fmtD(E.getTime())],
    ['평균임금 산정기간',`${fmtD(B.getTime())} ~ 퇴직일 전날 (${d3}일)`],
    ['3개월 임금 + 상여·연차 가산',C.won(total3)],
    [`1일 ${used}`,C.won(avg)],
    ['퇴직금 (세전)',C.won(pay),'sum'],
    [`퇴직소득세 (근속 ${taxYears}년 기준)`,'-'+C.won(t.tax),'minus'],
    ['지방소득세','-'+C.won(t.local),'minus'],
    ['세후 예상 수령액',C.won(net),'sum'],
    ['지급 기한 (퇴직 후 14일)',fmtD(due)]])}
  <p class="how">1일 ${used} ${C.won(avg)} × 30일 × ${C.fmt(days)}일 ÷ 365로 계산했습니다. 퇴직소득세는 근속연수공제와 환산급여공제를 적용한 어림값이며, IRP 계좌로 받으면 바로 떼지 않고 나중에 연금으로 받을 때 낮춰 냅니다.</p>`);
});
