from reject_moduleSL import RejectModule

print("세령이 등장!!!!!!!!!!!!!!!!!!!!!!!!!!")
print("검수도구__ver. 0.5")
print("단일 json 단위만 구현 완료 / 모듈화 / multi json 검수 추가예정")


base = r"C:\workspace\rejecter\extract_2022-08-01-16-09-39" ##//클립 바로 상위 폴더
# clip = "extract_2022-08-03-14-26-09_Clip_00042"

rej = RejectModule(base)

sum, full = rej.iterate_all() ## pandas df
