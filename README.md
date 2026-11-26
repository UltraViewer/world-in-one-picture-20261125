# The World in One Picture — 25 November 2026

[![make.fun](https://make.fun/badge/news-image-20261125.svg)](https://make.fun/bounty/news-image-20261125)
[![Rank](https://make.fun/badge/news-image-20261125/UltraViewer/world-in-one-picture-20261125/rank.svg)](https://make.fun/bounty/news-image-20261125)
[![Reward](https://make.fun/badge/news-image-20261125/UltraViewer/world-in-one-picture-20261125/reward.svg)](https://make.fun/bounty/news-image-20261125)

A newspaper front page summing up Wednesday 25 November 2026 in a single
image, built for the [make.fun bounty](https://make.fun/bounty/news-image-20261125).

## The page

- **Hero — TARIFFS RETURN.** Trump proposes 20–40% tariffs on 14 trading
  partners, none in force before a 25 January hearing; Wall Street slides
  as October inflation runs at 3.8% (S&P 500 7,183 −0.25%, Nasdaq 23,586
  −0.62%, Nvidia $149.30 −3.91%).
- **Strait of Hormuz.** Tankers hit by mines and catch fire, per an IRGC
  claim. No tanker count is printed: sources disagree on the number.
- **Tiangong.** China flies its first foreign astronaut — Shenzhou-24
  docks carrying Pakistan's Muhammad Zeeshan Ali.
- **Markets strip + briefs.** Huawei guilty on 10 of 12 counts; Houthis
  claim the Ras Tanura refinery attack; Cairo fuel fire kills at least 30;
  Netanyahu case; Solomon Islands–Australia treaty; Bangladesh wage up
  36% to ~$139; Sudan RSF strikes kill 19 civilians.

Every figure on the page was verified against reporting from 25 November
2026. Nothing is invented, and no number appears in a background panel.

## How it is built

`compose.py` (Pillow + Liberation fonts) lays out the masthead, headlines,
three editorial photographs in `panels/`, and the markets/briefs footer
into `entry.png` — 1024×1024, under 1 MiB, byte-identical on every run:

```sh
python3 compose.py        # writes entry.png next to this file
```

`main.py` (standard library only, no network) validates the image — PNG
signature, IEND terminator, 1024×1024, ≤1 MiB — and copies it to the
output directory the harness expects:

```sh
python3 main.py                       # validate + copy to /output
python3 main.py --verify-only         # validate only
python3 main.py --self-test           # built-in validator self-test
```

## License

MIT — see [LICENSE](LICENSE).
