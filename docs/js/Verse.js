import * as Shiki from "https://esm.sh/shiki@3.0.0";



const Cache = {
    // Lenka: This is from the mkdocs.yml `site_url`, if its changed, this needs to be updated as well. if there is a way to fetch this, lmk.
    SitePath: "/book/",
    AssetsPath: "/book/Assets/",
    // Lenka: Attribute to watch, this should never change (if it does get the new one from body tag from the rendered html).
    Attribute: "data-md-color-media",
    Grammar: null,
    Themes: {},
    CurrentTheme: null,
    VerseHighlighter: null
};

const GetThemePath = () => {
    const Scheme = document.body.getAttribute(Cache.Attribute);

    const bIsDark = Scheme === "(prefers-color-scheme: dark)" || (Scheme === "(prefers-color-scheme)" && window.matchMedia("(prefers-color-scheme: dark)").matches);

    const ThemeName = bIsDark ? "VerseDark" : "VerseLight";

    console.debug(`[VerseTheme.ThemePath]: ${ThemeName}.json (Attribute: ${Cache.Attribute} Scheme: ${Scheme})`);

    Cache.CurrentTheme = `${Cache.AssetsPath}${ThemeName}.json`;

    return Cache.CurrentTheme;
};

const VerseHighlighting = async () => {
    const Tasks = [];
    const ThemePath = GetThemePath();

    console.debug(`[VerseTheme.VerseHighlighting]: Starting Highlighting w/ ${ThemePath}`);

    if (!Cache.Grammar) {
        Tasks.push(fetch(`${Cache.AssetsPath}Verse.json`).then((Response) => Response.json()).then((JSON) => Cache.Grammar = JSON));
    }

    if (!Cache.Themes[ThemePath]) {
        Tasks.push(fetch(ThemePath).then((Response) => Response.json()).then((JSON) => Cache.Themes[ThemePath] = JSON));
    }

    if (Tasks.length > 0) {
        await Promise.all(Tasks);
    }

    if (!Cache.VerseHighlighter) {
        Cache.VerseHighlighter = await Shiki.createHighlighter({
            themes: [Cache.Themes[ThemePath]],
            langs: [Cache.Grammar]
        });
    } else {
        await Cache.VerseHighlighter.loadTheme(Cache.Themes[ThemePath]);
    }

    RenderVerseCodeBlocks();
};

const RenderVerseCodeBlocks = (ClassName = "code.language-verse") => {
    const VerseCodeBlocks = document.querySelectorAll(ClassName);

    console.debug(`[VerseTheme.RenderVerseCodeBlocks]: Rendering ${VerseCodeBlocks.length} blocks w/ class ${ClassName}`);

    console.time(`[VerseTheme.RenderVerseCodeBlocks]`);

    VerseCodeBlocks.forEach((Block) => {
        const Parent = Block.parentElement;
        const CodeContent = Block.textContent;

        const HTML = Cache.VerseHighlighter.codeToHtml(CodeContent, {
            lang: Cache.Grammar.name,
            theme: Cache.Themes[Cache.CurrentTheme].name
        });

        const TempDiv = document.createElement(`div`);
        TempDiv.innerHTML = HTML;

        const NewPre = TempDiv.firstElementChild;
        const NewCode = NewPre.querySelector(`code`);

        if (NewCode) {
            NewCode.classList.add(`language-verse`);
        }

        Parent.replaceWith(NewPre);
    });

    console.timeEnd(`[VerseTheme.RenderVerseCodeBlocks]`);
};

if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", VerseHighlighting);
} else {
    VerseHighlighting();
}

// Lenka: Might be a better way to do this, but it works for now.
const ThemeObserver = new MutationObserver(() => VerseHighlighting());
ThemeObserver.observe(document.body, {
    attributes: true,
    attributeFilter: [Cache.Attribute]
});