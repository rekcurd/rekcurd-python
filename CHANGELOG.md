# Change Log

## [v1.0.0](https://github.com/rekcurd/rekcurd-python/tree/v1.0.0) (2019-04-26)
[Full Changelog](https://github.com/rekcurd/rekcurd-python/compare/v0.4.5...v1.0.0)

**Implemented enhancements:**

- Large Evaluation data may cause OOM error [\#25](https://github.com/rekcurd/rekcurd-python/issues/25)
- Pipnize the packages [\#2](https://github.com/rekcurd/rekcurd-python/issues/2)

**Closed issues:**

- Delete Evaluation file [\#29](https://github.com/rekcurd/rekcurd-python/issues/29)

**Merged pull requests:**

- Update documents [\#47](https://github.com/rekcurd/rekcurd-python/pull/47) ([keigohtr](https://github.com/keigohtr))
- quit saving evaluate result as file [\#46](https://github.com/rekcurd/rekcurd-python/pull/46) ([yuki-mt](https://github.com/yuki-mt))
- prevent OOM due to evaluation data [\#44](https://github.com/rekcurd/rekcurd-python/pull/44) ([yuki-mt](https://github.com/yuki-mt))
- Pass object to update `predictor` [\#43](https://github.com/rekcurd/rekcurd-python/pull/43) ([keigohtr](https://github.com/keigohtr))
- Output error log [\#42](https://github.com/rekcurd/rekcurd-python/pull/42) ([keigohtr](https://github.com/keigohtr))
- Add `service\_insecure\_host` option [\#41](https://github.com/rekcurd/rekcurd-python/pull/41) ([keigohtr](https://github.com/keigohtr))
- Remove sqlalchemy library [\#40](https://github.com/rekcurd/rekcurd-python/pull/40) ([keigohtr](https://github.com/keigohtr))
- Use `SERVICE\_ID` instead `SERVICE\_NAME` [\#39](https://github.com/rekcurd/rekcurd-python/pull/39) ([keigohtr](https://github.com/keigohtr))
- Add AWS S3 data server [\#38](https://github.com/rekcurd/rekcurd-python/pull/38) ([keigohtr](https://github.com/keigohtr))
- Add template generation script [\#37](https://github.com/rekcurd/rekcurd-python/pull/37) ([keigohtr](https://github.com/keigohtr))
- Add dataserver, remove models [\#36](https://github.com/rekcurd/rekcurd-python/pull/36) ([keigohtr](https://github.com/keigohtr))
- add label to metrics [\#34](https://github.com/rekcurd/rekcurd-python/pull/34) ([yuki-mt](https://github.com/yuki-mt))
- fix type hinting [\#33](https://github.com/rekcurd/rekcurd-python/pull/33) ([yuki-mt](https://github.com/yuki-mt))
- Rename from `drucker` to `rekcurd` [\#32](https://github.com/rekcurd/rekcurd-python/pull/32) ([keigohtr](https://github.com/keigohtr))
- Rename repository link [\#31](https://github.com/rekcurd/rekcurd-python/pull/31) ([keigohtr](https://github.com/keigohtr))

## [v0.4.5](https://github.com/rekcurd/rekcurd-python/tree/v0.4.5) (2019-01-30)
[Full Changelog](https://github.com/rekcurd/rekcurd-python/compare/v0.4.4...v0.4.5)

**Merged pull requests:**

- Unittest py37 support [\#28](https://github.com/rekcurd/rekcurd-python/pull/28) ([keigohtr](https://github.com/keigohtr))

## [v0.4.4](https://github.com/rekcurd/rekcurd-python/tree/v0.4.4) (2019-01-15)
[Full Changelog](https://github.com/rekcurd/rekcurd-python/compare/v0.4.3...v0.4.4)

**Merged pull requests:**

- Add slack notification [\#26](https://github.com/rekcurd/rekcurd-python/pull/26) ([keigohtr](https://github.com/keigohtr))
- implement method for EvaluationResult protocol [\#24](https://github.com/rekcurd/rekcurd-python/pull/24) ([yuki-mt](https://github.com/yuki-mt))
- Close `open\(file\)` [\#23](https://github.com/rekcurd/rekcurd-python/pull/23) ([keigohtr](https://github.com/keigohtr))

## [v0.4.3](https://github.com/rekcurd/rekcurd-python/tree/v0.4.3) (2018-12-26)
[Full Changelog](https://github.com/rekcurd/rekcurd-python/compare/v0.4.2...v0.4.3)

**Merged pull requests:**

- Update README.md [\#22](https://github.com/rekcurd/rekcurd-python/pull/22) ([keigohtr](https://github.com/keigohtr))
- \[Hotfix\] fix ServiceEnvType if statement and make check strict [\#21](https://github.com/rekcurd/rekcurd-python/pull/21) ([yuki-mt](https://github.com/yuki-mt))
- separate evaluate and upload test data [\#20](https://github.com/rekcurd/rekcurd-python/pull/20) ([yuki-mt](https://github.com/yuki-mt))
- Istio support [\#19](https://github.com/rekcurd/rekcurd-python/pull/19) ([keigohtr](https://github.com/keigohtr))

## [v0.4.2](https://github.com/rekcurd/rekcurd-python/tree/v0.4.2) (2018-11-28)
[Full Changelog](https://github.com/rekcurd/rekcurd-python/compare/v0.4.1...v0.4.2)

**Closed issues:**

- Need file path check for saving ML model [\#16](https://github.com/rekcurd/rekcurd-python/issues/16)

**Merged pull requests:**

- Check if invalid filepath specified then raise Exception [\#17](https://github.com/rekcurd/rekcurd-python/pull/17) ([keigohtr](https://github.com/keigohtr))

## [v0.4.1](https://github.com/rekcurd/rekcurd-python/tree/v0.4.1) (2018-11-20)
[Full Changelog](https://github.com/rekcurd/rekcurd-python/compare/v0.4.0...v0.4.1)

**Merged pull requests:**

- Release prepare/v0.4.1 [\#15](https://github.com/rekcurd/rekcurd-python/pull/15) ([keigohtr](https://github.com/keigohtr))
- \[Hotfix\] Transform to string when `yaml.load` is boolean value [\#14](https://github.com/rekcurd/rekcurd-python/pull/14) ([keigohtr](https://github.com/keigohtr))
- \[Hotfix\] boolean checker [\#12](https://github.com/rekcurd/rekcurd-python/pull/12) ([keigohtr](https://github.com/keigohtr))
- evaluate model [\#11](https://github.com/rekcurd/rekcurd-python/pull/11) ([yuki-mt](https://github.com/yuki-mt))
- \[Hotfix\] Fix invalid variable [\#10](https://github.com/rekcurd/rekcurd-python/pull/10) ([keigohtr](https://github.com/keigohtr))

## [v0.4.0](https://github.com/rekcurd/rekcurd-python/tree/v0.4.0) (2018-11-07)
[Full Changelog](https://github.com/rekcurd/rekcurd-python/compare/v0.3.4...v0.4.0)

**Merged pull requests:**

- Add badge [\#9](https://github.com/rekcurd/rekcurd-python/pull/9) ([keigohtr](https://github.com/keigohtr))
- Create CONTRIBUTING.md [\#8](https://github.com/rekcurd/rekcurd-python/pull/8) ([syleeeee](https://github.com/syleeeee))
- Create CODE\_OF\_CONDUCT.md [\#7](https://github.com/rekcurd/rekcurd-python/pull/7) ([syleeeee](https://github.com/syleeeee))
- Pipnize drucker [\#6](https://github.com/rekcurd/rekcurd-python/pull/6) ([keigohtr](https://github.com/keigohtr))

## [v0.3.4](https://github.com/rekcurd/rekcurd-python/tree/v0.3.4) (2018-08-29)
[Full Changelog](https://github.com/rekcurd/rekcurd-python/compare/v0.3.3...v0.3.4)

## [v0.3.3](https://github.com/rekcurd/rekcurd-python/tree/v0.3.3) (2018-08-27)
[Full Changelog](https://github.com/rekcurd/rekcurd-python/compare/v0.3.2...v0.3.3)

**Merged pull requests:**

- Add sandbox env [\#5](https://github.com/rekcurd/rekcurd-python/pull/5) ([keigohtr](https://github.com/keigohtr))
- Refactor `sys.path.append` related code [\#3](https://github.com/rekcurd/rekcurd-python/pull/3) ([keigohtr](https://github.com/keigohtr))

## [v0.3.2](https://github.com/rekcurd/rekcurd-python/tree/v0.3.2) (2018-08-15)
[Full Changelog](https://github.com/rekcurd/rekcurd-python/compare/v0.3.1...v0.3.2)

## [v0.3.1](https://github.com/rekcurd/rekcurd-python/tree/v0.3.1) (2018-08-09)
[Full Changelog](https://github.com/rekcurd/rekcurd-python/compare/v0.3.0...v0.3.1)

**Merged pull requests:**

- \[Hotfix\] Change code generator [\#1](https://github.com/rekcurd/rekcurd-python/pull/1) ([keigohtr](https://github.com/keigohtr))

## [v0.3.0](https://github.com/rekcurd/rekcurd-python/tree/v0.3.0) (2018-07-18)
[Full Changelog](https://github.com/rekcurd/rekcurd-python/compare/v0.2.0...v0.3.0)

## [v0.2.0](https://github.com/rekcurd/rekcurd-python/tree/v0.2.0) (2018-07-17)


\* *This Change Log was automatically generated by [github_changelog_generator](https://github.com/skywinder/Github-Changelog-Generator)*