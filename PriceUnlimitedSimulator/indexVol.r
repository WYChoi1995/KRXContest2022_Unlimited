library(rmgarch)
library(rugarch)

baksetData = read.csv("C:/Users/WyChoi/PycharmProjects/KRXContest2022/Result/indexBasket.csv", row.names = "Date")
basketReal = na.omit(subset(data,select = c("BasketReal")))
basketSimulated = na.omit(subset(data,select = c("BasketSimulated")))

eGarchModel = ugarchspec(mean.model = list(armaOrder = c(0,0)), 
                         variance.model = list(garchOrder = c(1,1), model = "eGARCH"), 
                         distribution.model = "norm")

realFit = ugarchfit(spec=eGarchModel, data=basketReal)
simulatedFit = ugarchfit(spec=eGarchModel, data=basketSimulated)

sigmaData = data.frame(cbind(sigma(realFit), sigma(simulatedFit)))
colnames(sigmaData) = c("BasketReal", "BasketSimulated")

write.csv(sigmaData, "C:/Users/WyChoi/PycharmProjects/KRXContest2022/Result/sigmaIndexBasket.csv")
