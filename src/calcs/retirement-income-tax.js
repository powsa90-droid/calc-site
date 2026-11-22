// 소득세법 제48조·제55조 퇴직소득세 (2023년 이후 근속연수공제)
function retireTax(pay,y){
  let ded;
  if(y<=5)ded=1e6*y;else if(y<=10)ded=5e6+2e6*(y-5);else if(y<=20)ded=15e6+2.5e6*(y-10);else ded=40e6+3e6*(y-20);
  ded=Math.min(ded,pay);
  const conv=(pay-ded)*12/y;
  let cd;
  if(conv<=8e6)cd=conv;else if(conv<=7e7)cd=8e6+(conv-8e6)*0.6;else if(conv<=1e8)cd=45.2e6+(conv-7e7)*0.55;else if(conv<=3e8)cd=61.7e6+(conv-1e8)*0.45;else cd=151.7e6+(conv-3e8)*0.35;
  const base=Math.max(0,conv-cd);
  const b=[[14e6,.06,0],[5e7,.15,1.26e6],[8.8e7,.24,5.76e6],[1.5e8,.35,15.44e6],[3e8,.38,19.94e6],[5e8,.40,25.94e6],[1e9,.42,35.94e6],[Infinity,.45,65.94e6]];
  let conT=0,rate=0;for(const[l,r,k]of b)if(base<=l){conT=Math.max(0,base*r-k);rate=r;break}
  const tax=Math.floor(conT*y/12/10)*10;
  return{ded,conv,cd,base,conT,rate,tax,local:Math.floor(tax*0.1/10)*10};
}
function svcYears(sv,ev){ // 입사일~퇴직일(마지막 근무일 다음 날) 근속연수, 1년 미만 끝수는 1년
  const [a,b]=[sv,ev].map(v=>{const x=new Date(v);return{y:x.getUTCFullYear(),m:x.getUTCMonth(),d:x.getUTCDate()}});
  let mo=(b.y-a.y)*12+(b.m-a.m);let rem=b.d-a.d;if(rem<0){mo--;rem=1}
  return Math.max(1,Math.floor(mo/12)+((mo%12)||rem?1:0));
}
function d(v){const[y,m,dd]=v.split('-').map(Number);return Date.UTC(y,m-1,dd)}
C.onCalc(()=>{
  const pay=C.num('pay'),s=C.$('#start').value,e=C.$('#end').value;
  if(pay<=0||!s||!e){C.show('res','<p class="msg">퇴직금과 입사일, 퇴사일을 입력해 주세요.</p>');return}
  const days=Math.round((d(e)-d(s))/864e5)+1;
  if(days<=0){C.show('res','<p class="msg">퇴사일이 입사일보다 뒤여야 합니다.</p>');return}
  const y=svcYears(d(s),d(e)+864e5);
  const t=retireTax(pay,y);
  const total=t.tax+t.local;
  C.show('res',`<div class="big">퇴직소득세 + 지방소득세<b>${C.won(total)}</b></div>
  <div class="big" style="margin-top:6px">세후 수령액 ${C.won(pay-total)} · 실효세율 ${(total/pay*100).toFixed(2)}%</div>
  ${C.rows([
    ['① 퇴직소득',C.won(pay)],
    [`② 근속연수공제 (${y}년)`,'-'+C.won(t.ded),'minus'],
    ['③ 환산급여 (①−②) × 12 ÷ 근속연수',C.won(t.conv)],
    ['④ 환산급여공제','-'+C.won(t.cd),'minus'],
    [`⑤ 과세표준 (세율 ${t.rate*100}%)`,C.won(t.base)],
    ['⑥ 환산산출세액',C.won(t.conT)],
    ['⑦ 퇴직소득세 (⑥ × 근속연수 ÷ 12)',C.won(t.tax)],
    ['⑧ 지방소득세 (⑦ × 10%)',C.won(t.local)],
    ['납부할 세금 합계',C.won(total),'sum'],
    ['IRP 연금 수령 시 (1~10년차, 30% 감면)',C.won(Math.floor(total*0.7))]])}`);
});
