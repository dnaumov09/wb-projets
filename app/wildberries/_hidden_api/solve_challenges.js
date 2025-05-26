const puppeteer = require('puppeteer');
const fs = require('fs');

(async () => {
  const [scriptPath, payload] = process.argv.slice(2);

  const browser = await puppeteer.launch({ headless: true });
  // const page = await browser.newPage();

  // await page.setContent(`
  //   <html>
  //     <script src="https://antibot.wildberries.ru${scriptPath}"></script>
  //   </html>
  // `);

  // await page.waitForFunction(() => typeof window.solveChallenge === 'function');
  // const result = await page.evaluate(async (payload) => {
  //   const solution = await window.solveChallenge(payload);
  //   return solution;
  // }, payload);

  // await browser.close();
  // console.log(JSON.stringify(solution));
})();
