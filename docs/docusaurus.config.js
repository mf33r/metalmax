// Configuracao do site de documentacao do METAL MAX.
// Escrita a mao (sem gerador): menos uma dependencia que roda codigo nosso.
const { themes } = require('prism-react-renderer');

/** @type {import('@docusaurus/types').Config} */
const config = {
  title: 'METAL MAX',
  tagline: 'Jogo de plataforma em pygame-ce',
  favicon: 'img/favicon.svg',

  url: 'https://metalmax.local',
  baseUrl: '/',

  // A documentacao comeca na raiz do site: intro.md usa slug "/".
  onBrokenLinks: 'throw',
  onBrokenMarkdownLinks: 'warn',

  i18n: {
    defaultLocale: 'pt-BR',
    locales: ['pt-BR'],
  },

  presets: [
    [
      'classic',
      /** @type {import('@docusaurus/preset-classic').Options} */
      ({
        docs: {
          routeBasePath: '/',
          sidebarPath: require.resolve('./sidebars.js'),
        },
        blog: false,
        theme: {
          customCss: require.resolve('./src/css/custom.css'),
        },
      }),
    ],
  ],

  themeConfig:
    /** @type {import('@docusaurus/preset-classic').ThemeConfig} */
    ({
      colorMode: {
        defaultMode: 'dark',
        respectPrefersColorScheme: true,
      },
      navbar: {
        title: 'METAL MAX',
        items: [
          { type: 'docSidebar', sidebarId: 'documentacao', position: 'left', label: 'Documentação' },
          { to: '/estrutura', label: 'Estrutura', position: 'left' },
          { to: '/fisica', label: 'Física', position: 'left' },
        ],
      },
      footer: {
        style: 'dark',
        copyright: 'METAL MAX — documentação do projeto.',
      },
      prism: {
        theme: themes.github,
        darkTheme: themes.dracula,
        additionalLanguages: ['bash'],
      },
    }),
};

module.exports = config;
