(() => {
  'use strict';

  const element = id => document.getElementById(id);
  const scenarios = {
    store: {
      intro: 'What item and size are you looking for, and how many do you need?',
      examples: ['Do you have a blue cotton shirt in medium size?', 'I want two shirts, size M, for delivery next week.', 'Can your team confirm stock and delivery charges?'],
      fields: [
        ['item', /\b(?:shirts?|t-shirts?|trousers|jeans|shoes|dress(?:es)?|jackets?|sarees?|kurta(?:s)?|bags?)\b/i],
        ['size', /\b(?:size\s+(?:xs|s|m|l|xl|xxl|\d{1,2})|(?:extra small|small|medium|large|extra large)\s+size)\b/i],
        ['quantity', /\b(?:\d{1,3}|one|two|three|four|five|six|seven|eight|nine|ten)\s+(?:units?|pieces?|pcs|shirts?|t-shirts?|pairs?|dresses|jackets?|bags?)\b/i]
      ],
      review: 'A staff member can review stock, price and delivery before accepting an order.'
    },
    services: {
      intro: 'Which service do you need, in which area, and at what time?',
      examples: ['I need AC servicing tomorrow morning.', 'I am in Bengaluru, Koramangala. Is 11 AM possible?', 'Please send a quotation before booking.'],
      fields: [
        ['service', /\b(?:AC (?:servicing|repair)|plumbing|cleaning|electrical repair|installation|maintenance|pest control)\b/i],
        ['locality', /\b(?:Bengaluru|Bangalore|Delhi|Mumbai|Pune|Hyderabad|Chennai|Kolkata|Koramangala|Indiranagar|Lucknow|Azamgarh)\b/i],
        ['preferred time', /\b(?:morning|afternoon|evening|\d{1,2}(?::\d{2})?\s*(?:AM|PM))\b/i]
      ],
      review: 'A staff member can check the schedule and confirm any travel charges.'
    },
    realestate: {
      intro: 'Tell us what property you need, the locality and your budget.',
      examples: ['I want a 2 bedroom apartment to rent in Bengaluru.', 'My budget is ₹45,000 and I prefer Indiranagar.', 'Can I visit the property on Saturday afternoon?'],
      fields: [
        ['property type', /\b(?:apartment|flat|house|villa|plot|office|shop|commercial space)\b/i],
        ['locality', /\b(?:Bengaluru|Bangalore|Delhi|Mumbai|Pune|Hyderabad|Chennai|Kolkata|Koramangala|Indiranagar|Lucknow|Azamgarh)\b/i],
        ['budget', /(?:₹\s*\d[\d,]*|\b(?:INR|Rs\.?)\s*\d[\d,]*|\b\d[\d,.]*\s*(?:lakh|crore)\b)/i]
      ],
      review: 'An agent can check suitable listings and confirm any viewing request.'
    }
  };

  let scenario;
  let captured;
  let messages;
  let example;
  let handoff;

  function append(text, role) {
    const bubble = document.createElement('div');
    bubble.className = 'bubble ' + role;
    bubble.textContent = text;
    const conversation = element('conversation');
    conversation.append(bubble);
    conversation.scrollTop = conversation.scrollHeight;
  }

  function render() {
    const missing = scenario.fields.map(([name]) => name).filter(name => !captured.has(name));
    element('need').textContent = [...captured].map(([name, value]) => name + ': ' + value).join(' · ') || 'Waiting for enquiry details';
    element('missing').textContent = missing.join(', ') || 'All sample fields captured';
    element('stage').textContent = handoff ? 'Awaiting human review' :
      missing.length === 0 ? 'Qualified sample enquiry' : messages ? 'Qualification in progress' : 'New sample lead';
    element('next').textContent = handoff ? 'Staff review required' :
      missing.length ? 'Ask for ' + missing.join(', ') : 'Ready for staff review';
    element('counter').textContent = messages + ' sample message(s) processed';
    element('handoffResult').hidden = !handoff;
    return missing;
  }

  function reset() {
    const selector = element('scenario');
    scenario = scenarios[selector.value];
    captured = new Map();
    messages = 0;
    example = 0;
    handoff = false;
    element('type').textContent = selector.selectedOptions[0].textContent;
    element('conversation').replaceChildren();
    element('message').value = '';
    append(scenario.intro, 'bot');
    render();
  }

  function send() {
    const input = element('message');
    const message = input.value.trim().slice(0, 280);
    if (message.length < 5) {
      input.focus();
      return;
    }

    input.value = '';
    if (/\b(?:otp|one.time password|password|cvv|card number|bank details|upi pin|api key)\b/i.test(message)) {
      append('Please use sample details only. Keep passwords, verification codes and payment details out of the demo.', 'bot');
      return;
    }

    messages++;
    append(message, 'customer');
    if (/\b(?:refund|complaint|charged|paid|fraud|legal)\b/i.test(message)) {
      handoff = true;
      render();
      append('This request needs staff review. The demo cannot confirm payments, refunds or complaint outcomes.', 'bot');
      return;
    }

    for (const [name, pattern] of scenario.fields) {
      const match = message.match(pattern);
      if (match) captured.set(name, match[0]);
    }

    const missing = render();
    append(missing.length ? 'Thanks. Please share the ' + missing.join(', ') + '.' : scenario.review, 'bot');
  }

  element('handoffResult').textContent = 'Sample handoff flagged. A live deployment would notify the authorised team. This demo sends no messages.';
  element('scenario').addEventListener('change', reset);
  element('send').addEventListener('click', send);
  element('message').addEventListener('keydown', event => {
    if (event.key === 'Enter' && !event.isComposing) {
      event.preventDefault();
      send();
    }
  });
  element('example').addEventListener('click', () => {
    element('message').value = scenario.examples[example];
    example = (example + 1) % scenario.examples.length;
    element('message').focus();
  });
  element('handoff').addEventListener('click', () => {
    handoff = true;
    render();
  });
  element('resetAll').addEventListener('click', () => {
    element('scenario').value = 'store';
    reset();
  });
  reset();
})();
