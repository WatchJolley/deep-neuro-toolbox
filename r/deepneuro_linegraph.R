library(ggplot2)
library(lubridate)
library(dplyr)
library(boot)
library(broom)
library(gtable)
library(cowplot)
library(grid)


dir <- ".."
title = "games"
listOfGames <- c("private_eye","krull","crazy_climber","alien","asteroids","enduro","amidar","seaquest","kangaroo","atlantis","assault","skiing","frostbite","asterix","venture","ms_pacman","zaxxon","wizard_of_wor","yars_revenge","jamesbond","gravitar")
listOfModels <- c("LargeModel", "RecurrentLargeModel")
columnsPerGraph = 4
numOfRows = 5


#--------------------------------------------------------------------------------------

theme_set(theme_bw())

# create a function to take a resample of the values, 
# and then calculate the mean
boot_mean <- function(original_vector, resample_vector) {
  mean(original_vector[resample_vector])
}

idmaker = function(vec){
  return(paste(vec, collapse="-"))
}

allSame <- function(x) length(unique(x)) == 1

shift_legend <- function(p){
  
  # check if p is a valid object
  if(!"gtable" %in% class(p)){
    if("ggplot" %in% class(p)){
      gp <- ggplotGrob(p) # convert to grob
    } else {
      message("This is neither a ggplot object nor a grob generated from ggplotGrob. Returning original plot.")
      return(p)
    }
  } else {
    gp <- p
  }
  
  # check for unfilled facet panels
  facet.panels <- grep("^panel", gp[["layout"]][["name"]])
  empty.facet.panels <- sapply(facet.panels, function(i) "zeroGrob" %in% class(gp[["grobs"]][[i]]))
  empty.facet.panels <- facet.panels[empty.facet.panels]
  if(length(empty.facet.panels) == 0){
    message("There are no unfilled facet panels to shift legend into. Returning original plot.")
    return(p)
  }
  
  # establish extent of unfilled facet panels (including any axis cells in between)
  empty.facet.panels <- gp[["layout"]][empty.facet.panels, ]
  empty.facet.panels <- list(min(empty.facet.panels[["t"]]), min(empty.facet.panels[["l"]]),
                             max(empty.facet.panels[["b"]]), max(empty.facet.panels[["r"]]))
  names(empty.facet.panels) <- c("t", "l", "b", "r")
  
  # extract legend & copy over to location of unfilled facet panels
  guide.grob <- which(gp[["layout"]][["name"]] == "guide-box")
  if(length(guide.grob) == 0){
    message("There is no legend present. Returning original plot.")
    return(p)
  }
  gp <- gtable_add_grob(x = gp,
                        grobs = gp[["grobs"]][[guide.grob]],
                        t = empty.facet.panels[["t"]],
                        l = empty.facet.panels[["l"]],
                        b = empty.facet.panels[["b"]],
                        r = empty.facet.panels[["r"]],
                        name = "new-guide-box")
  
  # squash the original guide box's row / column (whichever applicable)
  # & empty its cell
  guide.grob <- gp[["layout"]][guide.grob, ]
  if(guide.grob[["l"]] == guide.grob[["r"]]){
    gp <- gtable_squash_cols(gp, cols = guide.grob[["l"]])
  }
  if(guide.grob[["t"]] == guide.grob[["b"]]){
    gp <- gtable_squash_rows(gp, rows = guide.grob[["t"]])
  }
  gp <- gtable_remove_grobs(gp, "guide-box")
  
  return(gp)
}

final1 <- c(0,0,0,0,0,0)
final2 <- c(0)

#--------------------------------------------------------------------------------------

for (game in listOfGames) {
  for (model in listOfModels) {
    
    location <- paste( dir, game, ".",model, "-all.csv", sep="")
    w1 <- read.csv(file=location,sep=",",head=TRUE)
    
    df<- c(0,0,0) 
    names(df)<-c("Run","Timesteps","Reward")
    w1 <- w1[,c("Runs","Iteration","TimestepsSoFar", "Truncated.Population.Elite.Validation.Reward.Mean")]
    
    for (r in unique(w1$Runs)) {
      temp <- filter(w1, Runs == r)
      temp <- approx(x=temp$TimestepsSoFar, y=temp$Truncated.Population.Elite.Validation.Reward.Mean, method = "linear", 
                     xout = c(5000000,10000000,15000000,20000000,25000000,30000000,35000000,40000000,45000000,50000000,55000000,60000000,65000000,70000000,75000000,80000000,85000000,90000000,95000000,100000000,105000000,110000000,115000000,120000000,125000000,130000000,135000000,140000000,145000000,150000000,155000000,160000000,165000000,170000000,175000000,180000000,185000000,190000000,195000000,200000000,205000000,210000000,215000000,220000000,225000000,230000000,235000000,240000000,245000000,250000000,255000000,260000000,265000000,270000000,275000000,280000000,285000000,290000000,295000000,300000000,305000000,310000000,315000000,320000000,325000000,330000000,335000000,340000000,345000000,350000000,355000000,360000000,365000000,370000000,375000000,380000000,385000000,390000000,395000000,400000000,405000000,410000000,415000000,420000000,425000000,430000000,435000000,440000000,445000000,450000000,455000000,460000000,465000000,470000000,475000000,480000000,485000000,490000000,495000000,500000000,505000000,510000000,515000000,520000000,525000000,530000000,535000000,540000000,545000000,550000000,555000000,560000000,565000000,570000000,575000000,580000000,585000000,590000000,595000000,600000000,605000000,610000000,615000000,620000000,625000000,630000000,635000000,640000000,645000000,650000000,655000000,660000000,665000000,670000000,675000000,680000000,685000000,690000000,695000000,700000000,705000000,710000000,715000000,720000000,725000000,730000000,735000000,740000000,745000000,750000000,755000000,760000000,765000000,770000000,775000000,780000000,785000000,790000000,795000000,800000000,805000000,810000000,815000000,820000000,825000000,830000000,835000000,840000000,845000000,850000000,855000000,860000000,865000000,870000000,875000000,880000000,885000000,890000000,895000000,900000000,905000000,910000000,915000000,920000000,925000000,930000000,935000000,940000000,945000000,950000000,955000000,960000000,965000000,970000000,975000000,980000000,985000000,990000000,995000000,1000000000),
                     rule = 1, f = 0, ties = mean)
      temp <- data.frame(r,temp$x,temp$y)
      names(temp)<-c("Run","Timesteps","Reward")
      df <- rbind(df, temp)
    }
    df = df[-1,]
    maxRewards <- max(w1$Truncated.Population.Elite.Validation.Reward.Mean)
    final.game    <- list(rep(game, length(df$Timesteps)))
    final.model   <- list(rep(model,length(df$Timesteps)))
    final.maxRewards <- list(rep(maxRewards,length(df$Timesteps)))
    mutiplelines <- data.frame(final.game,
                               final.model,
                               df$Run,
                               df$Timesteps,
                               df$Reward,
                               final.maxRewards)
    names(mutiplelines)<-c("Game","Model","Run","Timesteps","Reward","Max")
    mutiplelines$Timesteps <- mutiplelines$Timesteps*4
    mutiplelines$Timesteps <- mutiplelines$Timesteps/1e9
    
    final1 <- rbind(final1, mutiplelines)
    
    error.df<- c(0,0,0,0) 
    names(error.df)<-c("Timesteps","Reward","Left","Right")
    timesteps <- unique(df$Timesteps)
    
    for (t in timesteps) {
      temp <- filter(df, Timesteps == t)
      rewards <- na.omit(temp$Reward)
      rewards
      if (length(rewards) == 0){
        rewards<- c(0,0,0,0,0) 
      }
      if (allSame(rewards) == 1) {
        left  <- rewards[1]
        right <- rewards[1]
      } else {
        boot_rewards <- boot(rewards, boot_mean, R = 5000)
        boot_ci_rewards <- boot.ci(boot_rewards)
        left  <- boot_ci_rewards$percent[4]
        right <- boot_ci_rewards$percent[5]
      }
      temp <- data.frame(t,median(rewards),left,right)
      names(temp)<-c("Timesteps","Reward","Left","Right")
      error.df <- rbind(error.df, temp)
    }
    error.df <- na.omit(error.df)
    error.df$Timesteps <- error.df$Timesteps*4
    error.df$Timesteps <- error.df$Timesteps/1e9
    error.df
    error.df <- error.df[-1,]
    
    game.df   <- list(rep(game, length(error.df$Timesteps)))
    model.df  <- list(rep(model,length(error.df$Timesteps)))
    maxRewards <- list(rep(maxRewards,length(error.df$Timesteps)))
    full.df <- data.frame(game.df,model.df,error.df$Timesteps,error.df$Reward,error.df$Left,error.df$Right,maxRewards)
    names(full.df )<-c("Game",	"Model","Timesteps","Reward","Left","Right","Max")
    
    final2 <- rbind(final2, full.df)
  }
}

final2 <- final2[-1,]
final1 <- final1[-1,]
id = apply(as.matrix(final1[, c("Game", "Model", "Run")]), 1, idmaker)
final1 = cbind(final1, id)

lineTheme <- theme(
  axis.text.x = element_text(angle = 0, vjust=0.5),
  plot.title = element_text(hjust = 0.5),
  text =  element_text(size = 10, face="plain"),
  panel.grid.minor = element_blank(),  # turn off minor grid
  axis.title.y=element_blank(),
  axis.title.x = element_text(vjust=0),
  #legend.position = "none",
  strip.background = element_blank(),
  panel.border = element_rect(colour = "black"),
  plot.caption = element_text(hjust = 1, vjust=7, face = "italic") # move caption to the left
)

#--------------------------------------------------------------------------------------

# plot
plot1 <- ggplot(final1, aes(x=Timesteps, group=id, fill=Run)) +
  geom_line(aes(y=Reward, color=Model)) + 
  labs( 
    caption = "1e9",
    x="Number of Game Frames",
    y="", 
    color=NULL
  ) +  # title and caption 
  scale_x_continuous(breaks = seq(0, 4, by = 0.5)) +
  facet_wrap( ~ Game, ncol=columnsPerGraph, scales = "free_y" ) + 
  lineTheme


# plot
plot2 <- ggplot(final2, aes(x=Timesteps, fill=Model)) +
  geom_line(aes(y=Reward, color=Model)) + 
  geom_ribbon(aes(ymin=Left, ymax=Right), alpha=0.2) +
  labs( 
    caption = "1e9",
    x="Number of Game Frames",
    y="", 
    color=NULL
  ) +  # title and caption 
  scale_x_continuous(breaks = seq(0, 4, by = 0.5)) +
  geom_hline(aes(yintercept=final2$Max, color=final2$Model), lwd=1, lty=2) +
  facet_wrap( ~ Game, ncol=columnsPerGraph, scales = "free_y" ) + 
  lineTheme


grid.draw(shift_legend(plot2))

#--------------------------------------------------------------------------------------

myvars <- c("Game", "Model", "Max")
finaltable <- unique(final2[myvars])

file_write <- paste(dir, title, sep="")
file_write_plot1_pdf <- paste(file_write, "-lines.pdf", sep="")
file_write_plot2_pdf <- paste(file_write, "-mean.pdf", sep="")


ggsave(filename = file_write_plot1_pdf,  width = 3*columnsPerGraph, height = 3*numOfRows, units = "in", plot = plot1)
ggsave(filename = file_write_plot2_pdf,  width = 3*columnsPerGraph, height = 3*numOfRows, units = "in", plot = last_plot())