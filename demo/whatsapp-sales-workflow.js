(()=>{'use strict';
const $=id=>document.getElementById(id);
const data={
 store:{name:'Retail / product orders',intro:'Welcome! We can help with catalogue questions and order enquiries. What item and size are you looking for?',examples:['Do you have a blue cotton shirt in medium size?','I want two shirts, size M, for delivery next week.','Can your team confirm stock and delivery charges?'],intent:'Retail order enquiry'},
 services:{name:'Home and field services',intro:'Hello! Please tell us which service you need and your preferred day. A staff member confirms final availability.',examples:['I need AC servicing tomorrow morning.','I am in Bengaluru, Koramangala. Is 11 AM possible?','Please send a quotation before booking.'],intent:'Service and appointment enquiry'},
 realestate:{name:'Real Estate',intro:'Welcome! Are you looking to buy or rent? Share your property type, area and budget so the agent can help.',examples:['I want a 2 bedroom apartment to rent in Bengaluru.','My budget is ₹45,000 and I prefer Indiranagar.','Can I visit the property on Saturday afternoon?'],intent:'Property buyer or tenant enquiry'}
};
let scenario='store',step=0,count=0,handoff=false;
const make=(tag,t,cls)=>{let x=document.createElement(tag);x.textContent=t;if(cls)x.className=cls;return x};
const update=(key,val)=>{$(key).textContent=val};
const nice=q=>String(q||'').trim().slice(0,280);
function reply(q){
 const x=q.toLowerCase();
 if(/otp|password|card number|cvv|bank details/i.test(x))return 'For your security, please do not share passwords, OTPs or card details here. A verified team member can guide you through official channels.';
 if(/refund|complaint|legal|charged|paid|urgent fraud/i.test(x))return 'That needs a verified human review. I will flag this as a sample human-handoff requirement rather than inventing an answer.';
 if(scenario==='store'){
  if(step===1)return 'Thank you. How many units do you need? Your team’s approved catalogue and stock feed are needed to confirm exact sizes or availability.';
  if(step===2)return 'Got it. The request can now be recorded with item, size and quantity. A staff member should confirm stock, price and delivery before accepting an order.';
  return 'Your sample retail enquiry is ready for staff review. Real order processing and payments need an agreed shop/CRM integration.';
 }
 if(scenario==='services'){
  if(step===1)return 'Thanks. What is your area/locality and preferred time? We will treat this as a booking request until the staff calendar is checked.';
  if(step===2)return 'Thanks. The assistant could now send a booking request to the service team. Appointment availability, travel charges and final confirmation need the real business system.';
  return 'Your sample service enquiry is ready for human confirmation. No visit has actually been scheduled.';
 }
 if(step===1)return 'Thank you. Which locality do you prefer and what budget range should we consider? The agent’s approved listings will be needed for real matches.';
 if(step===2)return 'Understood. The buyer criteria can now be sent to the CRM for the agent to review verified listings and photos. Would you like a viewing request?';
 return 'The sample site-visit request is prepared for an agent. Actual property availability and calendar confirmation require live integrations.';
}
function append(message,kind){$('conversation').append(make('div',message,'bubble '+kind));$('conversation').scrollTop=$('conversation').scrollHeight}
function reset(){
 scenario=$('scenario').value;step=0;count=0;handoff=false;
 $('conversation').replaceChildren();append(data[scenario].intro,'bot');
 $('message').value='';$('handoffResult').hidden=true;
 update('type',data[scenario].name);update('need','Waiting for enquiry');update('stage','New sample lead');update('next','Needs qualification');update('counter','0 messages processed');
}
$('scenario').addEventListener('change',reset);
$('send').addEventListener('click',()=>{
 const q=nice($('message').value);
 if(q.length<5){$('message').focus();return}
 append(q,'customer');step++;count++;
 const answer=reply(q);append(answer,'bot');
 update('need',data[scenario].intent+': '+q.slice(0,75));
 update('stage',handoff?'Needs human review':step>=2?'Qualified sample enquiry':'Qualification in progress');
 update('next',handoff?'Staff approval required':step>=2?'Ready for staff handoff':'Need one more customer detail');
 update('counter',count+' sample message(s) processed');
 $('message').value='';
});
$('example').addEventListener('click',()=>{$('message').value=data[scenario].examples[Math.min(count,2)];$('message').focus()});
$('handoff').addEventListener('click',()=>{
 handoff=true;update('stage','Awaiting human review');update('next','Staff approval required');
 $('handoffResult').hidden=false;
 $('handoffResult').textContent='SAMPLE HANDOFF FLAGGED. A production version would notify the authorised team with consent and access controls. No person has been contacted by this demo.';
});
$('resetAll').addEventListener('click',()=>{$('scenario').value='store';reset()});
reset();
})();
