import { schedule } from '@netlify/functions';

// 🔥 SUBSTITUA A URL ABAIXO PELA SUA URL DO BUILD HOOK
const BUILD_HOOK = 'https://api.netlify.com/build_hooks/6a5780b8f3c0dd0918a96901';

export const handler = schedule('0 12 * * *', async () => {
  console.log('⏰ Executando build agendado...');
  
  try {
    const response = await fetch(BUILD_HOOK, { 
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      }
    });
    
    if (response.ok) {
      console.log('✅ Build triggered successfully!');
      return {
        statusCode: 200,
        body: JSON.stringify({ message: 'Build triggered successfully' })
      };
    } else {
      console.error('❌ Build trigger failed:', response.status);
      return {
        statusCode: response.status,
        body: JSON.stringify({ error: 'Build trigger failed' })
      };
    }
  } catch (error) {
    console.error('❌ Error:', error);
    return {
      statusCode: 500,
      body: JSON.stringify({ error: error.message })
    };
  }
});